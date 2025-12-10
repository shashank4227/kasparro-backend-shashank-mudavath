from datetime import datetime
import pytest
from pydantic import ValidationError
from schemas.ingestion import CoinGeckoEntry, CSVEntry

def test_coingecko_entry_valid():
    data = {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 50000.0,
        "market_cap": 1000000.0,
        "total_volume": 500000.0,
        "last_updated": datetime.now()
    }
    entry = CoinGeckoEntry(**data)
    assert entry.symbol == "BTC"  # Test validator
    assert entry.current_price == 50000.0

def test_coingecko_entry_invalid():
    data = {
        "id": "bitcoin",
        "symbol": "btc",
        # Missing name and current_price
    }
    with pytest.raises(ValidationError):
        CoinGeckoEntry(**data)

def test_csv_entry_valid():
    data = {
        "symbol": "eth",
        "price": 3000.0,
        "volume": 200000.0,
        "timestamp": datetime.now(),
        "source": "csv"
    }
    entry = CSVEntry(**data)
    assert entry.symbol == "ETH" # Test validator

def test_csv_entry_invalid_types():
    data = {
        "symbol": "eth",
        "price": "not-a-number", # Invalid type
        "volume": 200000.0,
        "timestamp": datetime.now(),
        "source": "csv"
    }
    with pytest.raises(ValidationError):
        CSVEntry(**data)
