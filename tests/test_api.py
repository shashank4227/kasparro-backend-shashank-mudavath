
# from fastapi.testclient import TestClient (removed)
from api.main import app

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Kasparro API is running. Check /docs for Swagger UI."}

def test_health_check(client):
    # Health check might fail if it tries to ping real DB inside the route logic 
    # if the route logic doesn't use the db session purely but does something else.
    # However, /health usually uses `db: Session = Depends(get_db)`.
    # So it should work with override.
    response = client.get("/health")
    # In SQLite, SELECT 1 works.
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_data_endpoint_pagination_error(client):
    response = client.get("/data?limit=1000") # Limit > 100
    assert response.status_code == 422

def test_data_endpoint_structure(client):
    response = client.get("/data")
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "api_latency_ms" in data
    assert "pagination" in data
    assert "data" in data

def test_pagination(client):
    response = client.get("/data?page=2&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["page"] == 2
    assert data["pagination"]["limit"] == 5

def test_invalid_pagination(client):
    # Test valid but out of bounds (handled by Pydantic ge/le)
    response = client.get("/data?limit=1000")
    assert response.status_code == 422
    
    response = client.get("/data?page=0")
    assert response.status_code == 422
