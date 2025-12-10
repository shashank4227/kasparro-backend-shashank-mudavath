from pydantic import BaseModel, HttpUrl, validator
from typing import Optional
from datetime import datetime

class CoinGeckoEntry(BaseModel):
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: Optional[float]
    total_volume: Optional[float]
    last_updated: Optional[datetime]

    @validator('symbol')
    def uppercase_symbol(cls, v):
        return v.upper()

class CoinPaprikaEntry(BaseModel):
    id: str
    symbol: str
    name: str
    quotes: dict
    last_updated: Optional[str]

    @validator('symbol')
    def uppercase_symbol(cls, v):
        return v.upper()
    
    @property
    def price_usd(self) -> float:
        return self.quotes.get("USD", {}).get("price", 0.0)
    
    @property
    def volume_24h(self) -> float:
        return self.quotes.get("USD", {}).get("volume_24h", 0.0)
    
    @property
    def market_cap(self) -> float:
        return self.quotes.get("USD", {}).get("market_cap", 0.0)
    
    @property
    def timestamp(self) -> datetime:
        if self.last_updated:
            try:
                # Format: 2018-06-12T13:41:00Z
                return datetime.strptime(self.last_updated, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                return datetime.now()
        return datetime.now()

class CSVEntry(BaseModel):
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    source: str

    @validator('symbol')
    def uppercase_symbol(cls, v):
        return v.upper()

class LegacyCSVEntry(BaseModel):
    Ticker: str
    LastPrice: float
    Vol: float
    RecordedDate: str

    @validator('Ticker')
    def uppercase_ticker(cls, v):
        return v.upper()

    def get_timestamp(self) -> datetime:
        # Parse custom format DD-MM-YYYY HH:MM:SS
        try:
            return datetime.strptime(self.RecordedDate, "%d-%m-%Y %H:%M:%S")
        except ValueError:
            return datetime.now()
