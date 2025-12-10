from fastapi import APIRouter, Depends, Query, Request
import time
from sqlalchemy.orm import Session
from typing import Optional
from api.dependencies import get_db
from schemas.api import CryptoDataResponse, CryptoData, PaginationResponse
from core.models import CryptoMarketData

router = APIRouter()

@router.get("/data", response_model=CryptoDataResponse)
def get_crypto_data(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    symbol: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CryptoMarketData)

    if symbol:
        query = query.filter(CryptoMarketData.symbol == symbol.upper())
    
    if source:
        query = query.filter(CryptoMarketData.source == source)

    total = query.count()
    
    data = query.order_by(CryptoMarketData.recorded_at.desc()) \
                .offset((page - 1) * limit) \
                .limit(limit) \
                .all()

    # Retrieve middleware data
    request_id = getattr(request.state, "request_id", "unknown")
    start_time = getattr(request.state, "start_time", time.time())
    latency = (time.time() - start_time) * 1000

    return CryptoDataResponse(
        request_id=request_id,
        api_latency_ms=latency,
        data=data,
        pagination=PaginationResponse(
            page=page,
            limit=limit,
            total=total
        )
    )
