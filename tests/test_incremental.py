from datetime import datetime
from core.models import CryptoMarketData, ETLCheckpoint, ETLRun, RawCoinGecko
from ingestion.ingest_api import ingest_coingecko_data
from ingestion.ingest_csv import ingest_csv_data
from unittest.mock import patch, MagicMock
import os
import pandas as pd

# Mock Data
MOCK_API_DATA = [
    {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 50000.0,
        "market_cap": 1000000.0,
        "total_volume": 500000.0,
        "last_updated": "2023-10-27T10:00:00Z"
    }
]

def test_api_idempotency(db_session):
    """
    Verify that running API ingestion twice with same data doesn't create duplicates.
    """
    with patch("ingestion.ingest_api.fetch_coingecko_data", return_value=MOCK_API_DATA):
        # First Run
        ingest_coingecko_data(db=db_session)
        assert db_session.query(CryptoMarketData).count() == 1
        assert db_session.query(ETLRun).count() == 1
        assert db_session.query(ETLRun).first().status == "success"

        # Second Run (Same Data)
        ingest_coingecko_data(db=db_session)
        
        # Should still be 1 record due to UniqueConstraint
        assert db_session.query(CryptoMarketData).count() == 1
        # Should be 2 runs tracked
        assert db_session.query(ETLRun).count() == 2

def test_api_checkpointing(db_session):
    """
    Verify that data older than checkpoint is skipped.
    """
    # Create a checkpoint in the future relative to our mock data
    cp = ETLCheckpoint(
        source_name="coingecko_api", 
        last_processed_at=datetime(2025, 1, 1) # Future date
    )
    db_session.add(cp)
    db_session.commit()

    with patch("ingestion.ingest_api.fetch_coingecko_data", return_value=MOCK_API_DATA):
        ingest_coingecko_data(db=db_session)
        
        # Should skip data because it's older than 2025
        assert db_session.query(CryptoMarketData).count() == 0
        
def test_csv_checkpointing(db_session, tmp_path):
    """
    Verify file-based checkpointing for CSVs.
    """
    # Create dummy CSV
    d = tmp_path / "test_data.csv"
    df = pd.DataFrame({
        "symbol": ["ETH"], "price": [3000.0], "volume": [100.0], 
        "timestamp": [datetime.now()], "source": ["csv"]
    })
    df.to_csv(d, index=False)
    filepath = str(d)

    # First Run
    ingest_csv_data(filepath, db=db_session)
    assert db_session.query(CryptoMarketData).count() == 1
    
    # Second Run
    ingest_csv_data(filepath, db=db_session)
    # Should skip entirely
    assert db_session.query(CryptoMarketData).count() == 1 
    
    # Verify skipped status in run log
    runs = db_session.query(ETLRun).filter(ETLRun.source == filepath).all()
    assert len(runs) == 2
    assert runs[1].status == "skipped"
