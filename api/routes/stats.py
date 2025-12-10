from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from api.dependencies import get_db
from core.models import ETLRun
from schemas.api import ETLRunResponse, ComparisonResponse, ComparisonReport
from typing import List, Optional

router = APIRouter()

@router.get("/stats")
def get_etl_stats(db: Session = Depends(get_db)):
    """
    Returns aggregated stats about ETL execution.
    """
    
    # Global Stats
    total_runs = db.query(ETLRun).count()
    total_records = db.query(func.sum(ETLRun.records_processed)).scalar() or 0
    failed_runs = db.query(ETLRun).filter(ETLRun.status == "failed").count()
    success_rate = 0
    if total_runs > 0:
        success_rate = ((total_runs - failed_runs) / total_runs) * 100

    # Per Source Stats
    stats_by_source = {}
    sources = db.query(ETLRun.source).distinct().all()
    source_names = [s[0] for s in sources]

    for source in source_names:
        last_run = db.query(ETLRun).filter(ETLRun.source == source).order_by(ETLRun.start_time.desc()).first()
        
        if last_run:
            duration_ms = None
            if last_run.end_time and last_run.start_time:
                duration_ms = (last_run.end_time - last_run.start_time).total_seconds() * 1000
            
            stats_by_source[source] = {
                "last_run_at": last_run.start_time,
                "last_status": last_run.status,
                "records_processed_last_run": last_run.records_processed,
                "duration_ms": duration_ms
            }

    return {
        "global_stats": {
            "total_runs": total_runs,
            "total_records_processed": total_records,
            "failed_runs": failed_runs,
            "success_rate_percent": round(success_rate, 2)
        },
        "sources": stats_by_source
    }

@router.get("/runs", response_model=List[ETLRunResponse])
def list_runs(
    limit: int = 10, 
    source: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """
    List recent ETL runs.
    """
    query = db.query(ETLRun)
    if source:
        query = query.filter(ETLRun.source == source)
    
    return query.order_by(ETLRun.start_time.desc()).limit(limit).all()

@router.get("/compare-runs", response_model=ComparisonResponse)
def compare_runs(threshold_percent: float = 20.0, db: Session = Depends(get_db)):
    """
    Detect anomalies by comparing the last 2 runs for each source.
    Flag if records_processed drops by more than `threshold_percent`.
    """
    reports = []
    anomalies = 0
    
    # Get all sources
    sources = db.query(ETLRun.source).distinct().all()
    source_names = [s[0] for s in sources]
    
    for source in source_names:
        # Get last 2 successful runs
        runs = db.query(ETLRun).filter(
            ETLRun.source == source, 
            ETLRun.status == "success"
        ).order_by(ETLRun.start_time.desc()).limit(2).all()
        
        if len(runs) < 2:
            continue
            
        current = runs[0]
        prev = runs[1]
        
        # Avoid division by zero
        if prev.records_processed == 0:
            change_pct = 100.0 if current.records_processed > 0 else 0.0
        else:
            change_pct = ((current.records_processed - prev.records_processed) / prev.records_processed) * 100
            
        # Check for DROP in volume (anomaly usually means missing data)
        # We can also check for massive spike, but usually drops are more concerning for reliability.
        is_anomaly = abs(change_pct) > threshold_percent
        
        if is_anomaly:
            anomalies += 1
            
        reports.append(ComparisonReport(
            source=source,
            current_run_id=current.id,
            current_records=current.records_processed,
            previous_run_id=prev.id,
            previous_records=prev.records_processed,
            change_percent=round(change_pct, 2),
            is_anomaly=is_anomaly
        ))
        
    return ComparisonResponse(
        anomalies_detected=anomalies,
        reports=reports
    )
