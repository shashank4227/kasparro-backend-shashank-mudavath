import requests
import os
from datetime import datetime
from core.database import SessionLocal
from core.models import RawCoinPaprika, CryptoMarketData, ETLCheckpoint, ETLRun
from schemas.ingestion import CoinPaprikaEntry
from services.resilience import RateLimiter, validation_retry

# CoinPaprika Free Tier
COINPAPRIKA_API_URL = "https://api.coinpaprika.com/v1/tickers"

# Rate Limiter (CoinPaprika is generous, but let's be safe: 1 call / sec)
rate_limiter = RateLimiter(calls_per_second=1.0)

@validation_retry()
def fetch_coinpaprika_data():
    rate_limiter.wait_for_token()
    params = {
        "limit": 10  # Just get top 10 for assignment
    }
    
    # Secure API Key Handling
    headers = {}
    api_key = os.getenv("COINPAPRIKA_API_KEY")
    if api_key:
        headers["Authorization"] = api_key 
    
    try:
        response = requests.get(COINPAPRIKA_API_URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching from CoinPaprika: {e}")
        raise e

def ingest_coinpaprika_data(db: SessionLocal = None):
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
        
    run_log = ETLRun(source="coinpaprika_api", status="running", start_time=datetime.now())
    db.add(run_log)
    db.commit()
    
    records_processed = 0
    source_name = "coinpaprika_api"
    
    try:
        # Checkpoint
        checkpoint = db.query(ETLCheckpoint).filter(ETLCheckpoint.source_name == source_name).first()
        
        data = fetch_coinpaprika_data()
        
        if not data:
            print("No data from CoinPaprika")
            run_log.status = "success"
            run_log.end_time = datetime.now()
            db.commit()
            return

        print(f"Fetched {len(data)} records from CoinPaprika")
        
        for entry in data:
            try:
                validated = CoinPaprikaEntry(**entry)
            except Exception as e:
                print(f"Skipping invalid CoinPaprika entry: {e}")
                continue
            
            # Raw Insert
            raw = RawCoinPaprika(
                coin_id=validated.id,
                data=entry
            )
            db.add(raw)
            
            # Idempotency Check
            record_time = validated.timestamp
            
            # Check against checkpoint
            if checkpoint and checkpoint.last_processed_at and record_time <= checkpoint.last_processed_at:
                continue

            # Check normalized existence
            exists = db.query(CryptoMarketData).filter(
                CryptoMarketData.symbol == validated.symbol,
                CryptoMarketData.source == source_name,
                CryptoMarketData.recorded_at == record_time
            ).first()
            
            if exists:
                continue
                
            normalized = CryptoMarketData(
                symbol=validated.symbol,
                price_usd=validated.price_usd,
                market_cap=validated.market_cap,
                volume_24h=validated.volume_24h,
                recorded_at=record_time,
                source=source_name
            )
            
            try:
                db.add(normalized)
                db.commit()
                records_processed += 1
            except Exception:
                db.rollback()
        
        # Update Checkpoint
        if records_processed > 0:
            if not checkpoint:
                checkpoint = ETLCheckpoint(source_name=source_name, last_processed_at=datetime.now())
                db.add(checkpoint)
            else:
                checkpoint.last_processed_at = datetime.now()
            db.commit()
            
        run_log.status = "success"
        run_log.records_processed = records_processed
        
    except Exception as e:
        run_log.status = "failed"
        run_log.error_message = str(e)
        print(f"CoinPaprika ETL Failed: {e}")
    finally:
        run_log.end_time = datetime.now()
        db.commit()
        if should_close:
            db.close()

if __name__ == "__main__":
    ingest_coinpaprika_data()
