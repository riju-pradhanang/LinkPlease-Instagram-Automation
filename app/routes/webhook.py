from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import WebhookPayload, WebhookResponse
from app.services.ingestion import process_webhook_event

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("", response_model=WebhookResponse)
def handle_webhook(payload: WebhookPayload, db: Session = Depends(get_db)):
    return process_webhook_event(db, payload)
