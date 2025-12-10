from services.drift_detection import detect_schema_drift
from ingestion.ingest_csv import ingest_csv_data
from core.models import ETLRun
import pytest
import pandas as pd

def test_drift_logic():
    expected = ["symbol", "price", "volume"]
    actual = ["symbol", "prce", "vol"] # typos/shortening
    
    report = detect_schema_drift(expected, actual)
    
    assert report["drift_detected"] == True
    assert len(report["matches"]) >= 1
    
    # Check match for price -> prce
    match_price = next((m for m in report["matches"] if m["expected"] == "price"), None)
    assert match_price is not None
    assert match_price["actual"] == "prce"
    assert match_price["confidence"] > 0.8

def test_ingestion_drift_logging(db_session, tmp_path):
    d = tmp_path / "drift_data.csv"
    # Create CSV with renamed column
    with open(d, "w") as f:
        f.write("symbol,prce,volume,timestamp,source\n") # 'price' -> 'prce'
        f.write("BTC,50000,100,2023-01-01,csv\n")

    ingest_csv_data(str(d), db=db_session)
    
    run = db_session.query(ETLRun).filter(ETLRun.source == str(d)).first()
    assert run.status == "success" # It should still succeed (partial/missing col handled by validation or skip)
    # But error message should contain warning
    assert run.error_message is not None
    assert "Potential rename" in run.error_message
    assert "prce" in run.error_message
