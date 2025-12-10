from core.models import ETLRun, CryptoMarketData
from datetime import datetime

def test_stats_endpoint(client, db_session):
    """
    Test /stats endpoint returns correct aggregation.
    """
    # Seed data
    db_session.add(ETLRun(source="test_src", status="success", records_processed=10, start_time=datetime.now()))
    db_session.add(ETLRun(source="test_src", status="failed", records_processed=0, start_time=datetime.now()))
    db_session.commit()

    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    
    assert data["global_stats"]["total_runs"] == 2
    assert data["global_stats"]["failed_runs"] == 1
    assert data["global_stats"]["total_records_processed"] == 10
    assert "test_src" in data["sources"]

def test_data_endpoint(client, db_session):
    """
    Test /data endpoint filtering and pagination.
    """
    # Seed data
    db_session.add(CryptoMarketData(
        symbol="BTC", price_usd=50000, volume_24h=100, 
        recorded_at=datetime.now(), source="src1"
    ))
    db_session.add(CryptoMarketData(
        symbol="ETH", price_usd=3000, volume_24h=100, 
        recorded_at=datetime.now(), source="src2"
    ))
    db_session.commit()

    # Test List
    response = client.get("/data")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2

    # Test Filter
    response = client.get("/data?symbol=BTC")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["symbol"] == "BTC"
    
    # Test Pagination
    response = client.get("/data?limit=1&skip=1")
    assert len(response.json()["data"]) == 1
