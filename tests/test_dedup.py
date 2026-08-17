import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import Rule
from app.schemas import WebhookPayload
from app.services.ingestion import process_webhook_event


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_unique_constraint_deduplication_race(db_session):
    # Setup test rule
    rule = Rule(keyword="link", response_link="https://example.com/item")
    db_session.add(rule)
    db_session.commit()

    payload = WebhookPayload(
        event_id="evt_12345",
        user_id="usr_999",
        comment_text="Please send me the link!"
    )

    # First event ingestion
    res1 = process_webhook_event(db_session, payload)
    assert res1.status == "processed"
    assert res1.job_created is True

    # Duplicate event ingestion with identical event_id (Simulating race condition / re-delivery)
    res2 = process_webhook_event(db_session, payload)
    assert res2.status == "duplicate"
    assert res2.job_created is False
    assert res2.message == "Event already processed"
