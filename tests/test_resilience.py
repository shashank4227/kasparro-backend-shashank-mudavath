import time
import requests
from unittest.mock import patch, MagicMock
from services.resilience import RateLimiter, validation_retry
from ingestion.ingest_api import fetch_coingecko_data
import pytest

def test_rate_limiter():
    """
    Verify that RateLimiter forces a delay.
    """
    limiter = RateLimiter(calls_per_second=10) # 0.1s interval
    
    start = time.time()
    limiter.wait_for_token()
    limiter.wait_for_token()
    limiter.wait_for_token()
    end = time.time()
    
    # Should take at least 0.2s (first call immediate, next 2 wait 0.1s each)
    assert (end - start) >= 0.18

def test_retry_on_failure():
    """
    Verify that fetch_coingecko_data retries on failure.
    """
    # We mock requests.get to fail twice then succeed
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": "bitcoin"}]
    mock_response.raise_for_status = MagicMock()
    
    with patch("requests.get") as mock_get:
        # Side effect: ConnectionError, ConnectionError, SuccessResponse
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Fail 1"),
            requests.exceptions.ConnectionError("Fail 2"),
            mock_response
        ]
        
        # We also need to patch RateLimiter.wait_for_token to avoid sleeping in tests
        with patch("services.resilience.RateLimiter.wait_for_token"):
            data = fetch_coingecko_data()
            
            assert len(data) == 1
            assert mock_get.call_count == 3 # 2 fails + 1 success
