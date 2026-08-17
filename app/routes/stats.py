from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import WebhookEvent, Rule, SendJob
from app.schemas import StatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total_events = db.query(WebhookEvent).count()
    total_rules = db.query(Rule).count()
    total_jobs = db.query(SendJob).count()
    pending_jobs = db.query(SendJob).filter(SendJob.status == "PENDING").count()
    successful_jobs = db.query(SendJob).filter(SendJob.status == "SUCCESS").count()
    failed_jobs = db.query(SendJob).filter(SendJob.status == "FAILED").count()

    return StatsResponse(
        total_events=total_events,
        total_rules=total_rules,
        total_jobs=total_jobs,
        pending_jobs=pending_jobs,
        successful_jobs=successful_jobs,
        failed_jobs=failed_jobs
    )
