import pandas as pd
from datetime import datetime
from core.database import SessionLocal
from core.models import RawLegacyUpload, CryptoMarketData, ETLCheckpoint, ETLRun
from schemas.ingestion import LegacyCSVEntry

def ingest_legacy_data(filepath, db: SessionLocal = None):
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    
    run_log = ETLRun(source=filepath, status="running", start_time=datetime.now())
    db.add(run_log)
    db.commit()

    records_processed = 0
    try:
        # Checkpoint check
        checkpoint = db.query(ETLCheckpoint).filter(ETLCheckpoint.source_name == filepath).first()
        if checkpoint:
            print(f"Legacy File {filepath} already processed. Skipping.")
            run_log.status = "skipped"
            return

        try:
            df = pd.read_csv(filepath)
            print(f"Read {len(df)} rows from {filepath}")
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            run_log.status = "failed"
            return

        for _, row in df.iterrows():
            try:
                row_dict = row.to_dict()
                validated_data = LegacyCSVEntry(**row_dict)
            except Exception as e:
                 print(f"Skipping invalid Legacy CSV row: {e}")
                 continue

            raw_record = RawLegacyUpload(
                filename=filepath,
                ticker=validated_data.Ticker,
                last_price=validated_data.LastPrice,
                vol=validated_data.Vol,
                recorded_date=validated_data.RecordedDate
            )
            db.add(raw_record)

            normalized_record = CryptoMarketData(
                symbol=validated_data.Ticker,   
                price_usd=validated_data.LastPrice, 
                market_cap=None,
                volume_24h=validated_data.Vol,  
                recorded_at=validated_data.get_timestamp(), 
                source="legacy_csv"
            )
            
            try:
                db.add(normalized_record)
                db.commit()
                records_processed += 1
            except Exception:
                db.rollback()

        if records_processed > 0:
            db.add(ETLCheckpoint(source_name=filepath, last_processed_at=datetime.now()))
            try:
                db.commit()
                print(f"Successfully processed {records_processed} legacy records.")
            except Exception:
                pass
        
        run_log.status = "success"
        run_log.records_processed = records_processed

    except Exception as e:
        run_log.status = "failed"
        run_log.error_message = str(e)
    finally:
        run_log.end_time = datetime.now()
        try:
            db.commit()
        except:
            pass
        if should_close:
            db.close()

if __name__ == "__main__":
    ingest_legacy_data("legacy_crypto_data.csv")
