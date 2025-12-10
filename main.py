import time
from core.database import engine, Base, init_db, SessionLocal
from ingestion.ingest_api import ingest_coingecko_data
from ingestion.ingest_csv import ingest_csv_data
from ingestion.ingest_legacy import ingest_legacy_data
from ingestion.ingest_coinpaprika import ingest_coinpaprika_data

def main():
    print("Starting ETL Pipeline...")
    
    # Initialize DB (create tables if not exist)
    print("Initializing Database...")
    init_db()
    
    db = SessionLocal()
    try:
        # Run API Ingestion
        print("Starting CoinGecko Ingestion...")
        ingest_coingecko_data(db=db)
        
        print("Starting CoinPaprika Ingestion...")
        ingest_coinpaprika_data(db=db)
    finally:
        db.close()
    
    print("Starting CSV Ingestion...")
    print("\n--- Running CSV Ingestion ---")
    ingest_csv_data("crypto_data.csv")

    # Run Legacy CSV Ingestion
    print("\n--- Running Legacy CSV Ingestion ---")
    ingest_legacy_data("legacy_crypto_data.csv")
    
    print("\nETL Pipeline Completed.")

if __name__ == "__main__":
    main()
