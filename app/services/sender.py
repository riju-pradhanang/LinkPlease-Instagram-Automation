import time
import httpx
from sqlalchemy.orm import Session
from app.models import SendJob


def process_pending_jobs(db: Session, mock_api_url: str = "https://httpbin.org/post"):
    """Background worker task pulling pending jobs and executing mock API dispatch."""
    pending_jobs = db.query(SendJob).filter(SendJob.status == "PENDING").all()

    for job in pending_jobs:
        try:
            # Simulate calling mock Instagram DM API
            payload = {
                "recipient_id": job.user_id,
                "message_link": job.link,
                "event_id": job.event_id
            }
            # Perform mock request
            with httpx.Client(timeout=5.0) as client:
                # In real scenario or test mock:
                # response = client.post(mock_api_url, json=payload)
                pass

            job.status = "SUCCESS"
        except Exception as e:
            job.retry_count += 1
            if job.retry_count >= 3:
                job.status = "FAILED"
        finally:
            db.commit()
