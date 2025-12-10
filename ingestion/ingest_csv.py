import pandas as pd
from datetime import datetime
from core.database import SessionLocal
from core.models import RawCSVUpload, CryptoMarketData, ETLCheckpoint, ETLRun
from schemas.ingestion import CSVEntry
from services.drift_detection import detect_schema_drift

def ingest_csv_data(filepath, db: SessionLocal = None):
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
            print(f"File {filepath} already processed. Skipping.")
            run_log.status = "skipped"
            return # finally block will commit

        try:
            df = pd.read_csv(filepath)
            print(f"Read {len(df)} rows from {filepath}")
            
            # Check for Drift
            expected_cols = list(CSVEntry.__fields__.keys())
            drift_report = detect_schema_drift(expected_cols, list(df.columns))
            
            if drift_report["drift_detected"]:
                print(f"WARNING: Schema Drift Detected in {filepath}")
                if drift_report["matches"]:
                    for match in drift_report["matches"]:
                        msg = f"Potential rename: '{match['expected']}' -> '{match['actual']}' (conf: {match['confidence']})"
                        print(msg)
                        run_log.error_message = (run_log.error_message or "") + msg + "; "
                
                if drift_report["missing"] and not drift_report["matches"]:
                     msg = f"Missing columns: {drift_report['missing']}"
                     print(msg)
                     run_log.error_message = (run_log.error_message or "") + msg + "; "
            
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            run_log.status = "failed"
            run_log.error_message = "File not found"
            return

        for _, row in df.iterrows():
            try:
                row_dict = row.to_dict()
                validated_data = CSVEntry(**row_dict)
            except Exception as e:
                 print(f"Skipping invalid CSV row: {e}")
                 continue

            raw_record = RawCSVUpload(
                filename=filepath,
                symbol=validated_data.symbol,
                price=validated_data.price,
                volume=validated_data.volume,
                timestamp=validated_data.timestamp,
                source=validated_data.source
            )
            db.add(raw_record)

            normalized_record = CryptoMarketData(
                symbol=validated_data.symbol,
                price_usd=validated_data.price,
                market_cap=None, 
                volume_24h=validated_data.volume,
                recorded_at=validated_data.timestamp,
                source="csv_upload"
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
                print(f"Successfully processed {records_processed} records from {filepath}")
            except Exception as e:
                 print(f"Error saving checkpoint: {e}")
        
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
    ingest_csv_data("crypto_data.csv")
