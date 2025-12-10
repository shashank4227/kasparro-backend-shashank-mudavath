from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Header
from core.database import SessionLocal
from ingestion.ingest_api import ingest_coingecko_data
from ingestion.ingest_coinpaprika import ingest_coinpaprika_data
from ingestion.ingest_csv import ingest_csv_data
from ingestion.ingest_legacy import ingest_legacy_data
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)

async def verify_admin_secret(x_admin_secret: str = Header(...)):
    expected_secret = os.getenv("ADMIN_SECRET", "default_insecure_secret")
    if x_admin_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Invalid Admin Secret")

def run_etl_pipeline():
    """
    Executes the full ETL pipeline.
    This function is designed to run in the background.
    """
    logger.info("Starting Manual ETL Trigger...")
    db = SessionLocal()
    try:
        # API Ingestion
        ingest_coingecko_data(db=db)
        ingest_coinpaprika_data(db=db)
    except Exception as e:
        logger.error(f"Error in API Ingestion: {e}")
    finally:
        db.close()
    
    # CSV Ingestion
    try:
        ingest_csv_data("crypto_data.csv")
        ingest_legacy_data("legacy_crypto_data.csv")
    except Exception as e:
        logger.error(f"Error in CSV Ingestion: {e}")
        
    logger.info("Manual ETL Trigger Completed.")

@router.post("/trigger-etl", dependencies=[Depends(verify_admin_secret)])
async def trigger_etl(background_tasks: BackgroundTasks):
    """
    Manually triggers the ETL pipeline.
    Protected by X-Admin-Secret header.
    """
    background_tasks.add_task(run_etl_pipeline)
    return {"message": "ETL pipeline triggered in background"}
