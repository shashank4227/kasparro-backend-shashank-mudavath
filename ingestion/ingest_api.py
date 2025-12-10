import requests
import os
from datetime import datetime
from core.database import SessionLocal
from core.models import RawCoinGecko, CryptoMarketData, ETLCheckpoint, ETLRun
from schemas.ingestion import CoinGeckoEntry
from services.resilience import RateLimiter, validation_retry

# Rate Limiter (e.g., 1 call every 2 seconds -> 0.5 calls/sec)
rate_limiter = RateLimiter(calls_per_second=0.5)

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"

@validation_retry()
def fetch_coingecko_data():
    rate_limiter.wait_for_token()
    
    # Secure API Key Handling
    api_key = os.getenv("COINGECKO_API_KEY")
    headers = {}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": "false"
    }
    try:
        response = requests.get(COINGECKO_API_URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from CoinGecko: {e}")
        raise e # Re-raise to trigger retry

def ingest_coingecko_data(db: SessionLocal = None, simulate_failure_after: int = -1):
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    
    # Start Run Log
    run_log = ETLRun(source="coingecko_api", status="running", start_time=datetime.now())
    db.add(run_log)
    db.commit() # Get ID
    
    records_processed = 0
    
    try:
        # Check Checkpoint
        source_name = "coingecko_api"
        checkpoint = db.query(ETLCheckpoint).filter(ETLCheckpoint.source_name == source_name).first()
        
        data = fetch_coingecko_data()

        if not data:
            print("No data received from CoinGecko.")
            run_log.status = "success"
            run_log.end_time = datetime.now()
            db.commit()
            db.close()
            return

        print(f"Fetched {len(data)} records from CoinGecko.")

        for entry in data:
            try:
                validated_data = CoinGeckoEntry(**entry)
            except Exception as e:
                print(f"Skipping invalid data entry: {e}")
                continue

            raw_record = RawCoinGecko(
                coin_id=validated_data.id,
                data=entry
            )
            db.add(raw_record)
            
            exists = db.query(CryptoMarketData).filter(
                CryptoMarketData.symbol == validated_data.symbol,
                CryptoMarketData.source == source_name,
            ).count() > 0

            record_time = validated_data.last_updated if validated_data.last_updated else datetime.now()

            if checkpoint and checkpoint.last_processed_at and record_time <= checkpoint.last_processed_at:
                 continue

            normalized_record = CryptoMarketData(
                symbol=validated_data.symbol,
                price_usd=validated_data.current_price,
                market_cap=validated_data.market_cap,
                volume_24h=validated_data.total_volume,
                recorded_at=record_time,
                source=source_name
            )
            
            try:
                db.add(normalized_record)
                db.commit()
                records_processed += 1
                
                # Failure Injection
                if simulate_failure_after > 0 and records_processed >= simulate_failure_after:
                    raise Exception("Simulated Failure Injection")
                    
            except Exception as e:
                db.rollback()
                if "Simulated Failure Injection" in str(e):
                    raise e # Propagate crucial failures

        # Update Checkpoint
        if records_processed > 0:
            if not checkpoint:
                checkpoint = ETLCheckpoint(source_name=source_name, last_processed_at=datetime.now())
                db.add(checkpoint)
            else:
                checkpoint.last_processed_at = datetime.now()
            try:
                db.commit()
            except Exception as e:
                print(f"Error updating checkpoint: {e}")
        
        run_log.status = "success"
        run_log.records_processed = records_processed

    except Exception as e:
        run_log.status = "failed"
        run_log.error_message = str(e)
        print(f"ETL Failed: {e}")
    finally:
        run_log.end_time = datetime.now()
        try:
            db.commit()
        except:
            pass
        if should_close:
            db.close()

if __name__ == "__main__":
    ingest_coingecko_data()
