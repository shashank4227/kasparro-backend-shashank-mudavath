from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class HealthCheck(BaseModel):
    status: str
    db_connection: bool
    etl_last_run: Optional[datetime]

class CryptoData(BaseModel):
    symbol: str
    price_usd: float
    market_cap: Optional[float]
    volume_24h: Optional[float]
    recorded_at: datetime
    source: str

    class Config:
        from_attributes = True

class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int

class CryptoDataResponse(BaseModel):
    request_id: str
    api_latency_ms: float
    data: List[CryptoData]
    pagination: PaginationResponse

class ETLRunResponse(BaseModel):
    id: int
    source: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    records_processed: int
    error_message: Optional[str]

    class Config:
        from_attributes = True

class ComparisonReport(BaseModel):
    source: str
    current_run_id: int
    current_records: int
    previous_run_id: int
    previous_records: int
    change_percent: float
    is_anomaly: bool

class ComparisonResponse(BaseModel):
    anomalies_detected: int
    reports: List[ComparisonReport]
