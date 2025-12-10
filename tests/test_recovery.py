from ingestion.ingest_api import ingest_coingecko_data
from core.models import CryptoMarketData, ETLRun, ETLCheckpoint
from unittest.mock import patch
import pytest

MOCK_DATA = [
    {"id": f"coin_{i}", "symbol": f"C{i}", "name": f"Coin {i}", "current_price": 100.0, "market_cap": 1000.0, "total_volume": 500.0, "last_updated": "2023-10-27T10:00:00Z"}
    for i in range(10) # 10 records
]

def test_failure_recovery_flow(db_session):
    """
    Test that pipeline can crash mid-way and resume without duplicates.
    """
    with patch("ingestion.ingest_api.fetch_coingecko_data", return_value=MOCK_DATA):
        
        # 1. Failure Run (Crash after 5 records)
        print("\n--- Starting Failure Run ---")
        try:
            ingest_coingecko_data(db=db_session, simulate_failure_after=5)
        except Exception as e:
            assert "Simulated Failure Injection" in str(e)
        
        # Verify Partial State
        assert db_session.query(CryptoMarketData).count() == 5
        failed_run = db_session.query(ETLRun).filter(ETLRun.status == "failed").first()
        assert failed_run is not None
        assert "Simulated Failure Injection" in failed_run.error_message
        
        # 2. Recovery Run (Run to completion)
        print("\n--- Starting Recovery Run ---")
        ingest_coingecko_data(db=db_session)
        
        # Verify Final State
        # Should have 10 records total (5 old + 5 new)
        assert db_session.query(CryptoMarketData).count() == 10
        
        # Verify no duplicates were created for the first 5 (implied by count=10 if unique constraint works, checking specifically for C0)
        assert db_session.query(CryptoMarketData).filter(CryptoMarketData.symbol == "C0").count() == 1
        
        # Verify Success Run
        success_run = db_session.query(ETLRun).filter(ETLRun.status == "success").order_by(ETLRun.start_time.desc()).first()
        assert success_run is not None
        # In the recovery run, it might skip the first 5 if checkpoint was updated?
        # Actually logic: checkpoint is updated AFTER loop if records > 0.
        # But failure happened inside loop. Checkpoint likely NOT updated for the partial run depending on logic placement.
        # Let's check logic: "Update Checkpoint" is AFTER loop.
        # So on failure, checkpoint is NOT updated.
        # So recovery run sees NO checkpoint (or old one).
        # It tries to insert C0 again. UniqueConstraint violation -> rollback -> continue.
        # It inserts C5..C9 successfully.
        # So records_processed in run 2 should be 5.
        
        assert success_run.records_processed == 5
