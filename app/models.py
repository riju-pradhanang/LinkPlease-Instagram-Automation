from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint
from app.db import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False, index=True)
    response_link = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(String, nullable=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SendJob(Base):
    __tablename__ = "send_jobs"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False)
    link = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, SUCCESS, FAILED
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
