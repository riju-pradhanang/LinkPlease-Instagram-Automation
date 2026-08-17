from sqlalchemy import (
    Column, String, Text, Integer, BigInteger, TIMESTAMP,
    ForeignKey, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from app.db import Base


class Rule(Base):
    __tablename__ = "rules"
    rule_id = Column(String, primary_key=True)
    keyword = Column(Text, nullable=False)
    dm_message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Event(Base):
    __tablename__ = "events"
    event_id = Column(String, primary_key=True)
    event_type = Column(Text, nullable=False)
    comment_id = Column(Text)
    post_id = Column(Text)
    comment_text = Column(Text)
    from_user_id = Column(Text)
    from_username = Column(Text)
    sent_at = Column(TIMESTAMP(timezone=True))
    received_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    raw_payload = Column(JSONB, nullable=False)


class SendJob(Base):
    __tablename__ = "send_jobs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    rule_id = Column(String, ForeignKey("rules.rule_id"), nullable=False)
    recipient_user_id = Column(Text, nullable=False)
    comment_id = Column(Text)
    dm_message = Column(Text, nullable=False)
    status = Column(Text, nullable=False, server_default="pending")
    dm_id = Column(Text)
    attempts = Column(Integer, nullable=False, server_default="0")
    next_attempt_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("rule_id", "recipient_user_id", name="uq_rule_user"),)


class StatsCounter(Base):
    __tablename__ = "stats_counters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    duplicates_blocked = Column(BigInteger, nullable=False, server_default="0")