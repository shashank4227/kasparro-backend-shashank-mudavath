from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from api.dependencies import get_db
from schemas.api import HealthCheck
from core.models import CryptoMarketData

router = APIRouter()

@router.get("/health", response_model=HealthCheck)
def health_check(db: Session = Depends(get_db)):
    db_status = False
    try:
        db.execute(text("SELECT 1"))
        db_status = True
    except Exception:
        db_status = False

    last_run = db.query(func.max(CryptoMarketData.created_at)).scalar()

    return HealthCheck(
        status="healthy" if db_status else "unhealthy",
        db_connection=db_status,
        etl_last_run=last_run
    )
