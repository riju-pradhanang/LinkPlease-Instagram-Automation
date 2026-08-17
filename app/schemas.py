from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RuleCreate(BaseModel):
    keyword: str
    response_link: str


class RuleResponse(BaseModel):
    id: int
    keyword: str
    response_link: str
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookPayload(BaseModel):
    event_id: str
    user_id: str
    comment_text: str


class WebhookResponse(BaseModel):
    status: str
    event_id: str
    job_created: bool
    message: Optional[str] = None


class StatsResponse(BaseModel):
    total_events: int
    total_rules: int
    total_jobs: int
    pending_jobs: int
    successful_jobs: int
    failed_jobs: int
