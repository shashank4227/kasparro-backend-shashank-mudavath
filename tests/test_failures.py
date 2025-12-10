from ingestion.ingest_csv import ingest_csv_data
from core.models import ETLRun
import pandas as pd
import pytest

def test_file_not_found(db_session):
    """
    Test behavior when CSV file does not exist.
    """
    ingest_csv_data("non_existent_file.csv", db=db_session)
    
    run = db_session.query(ETLRun).filter(ETLRun.source == "non_existent_file.csv").first()
    assert run is not None
    assert run.status == "failed"
    assert "File not found" in run.error_message

def test_csv_schema_mismatch(db_session, tmp_path):
    """
    Test behavior when CSV has invalid data types (e.g. string for price).
    The row should be skipped, but the run should succeed (partial success).
    """
    d = tmp_path / "bad_data.csv"
    # Create CSV with one valid and one invalid row
    with open(d, "w") as f:
        f.write("symbol,price,volume,timestamp,source\n")
        f.write("BTC,50000,100,2023-01-01,csv\n")
        f.write("ETH,not-a-number,100,2023-01-01,csv\n") # Invalid price

    ingest_csv_data(str(d), db=db_session)
    
    run = db_session.query(ETLRun).filter(ETLRun.source == str(d)).first()
    assert run.status == "success"
    # Only 1 record should be processed
    assert run.records_processed == 1
