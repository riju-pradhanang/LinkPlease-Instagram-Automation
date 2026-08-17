import asyncio
import time
from collections import deque
from datetime import datetime, timedelta, timezone
import httpx
from sqlalchemy import select, update
from app.config import PSEUDOGRAM_API_KEY, PSEUDOGRAM_BASE_URL
from app.db import AsyncSessionLocal
from app.models import SendJob

MAX_ATTEMPTS = 6
_request_times = deque(maxlen=10)


def backoff_seconds(attempts: int) -> int:
    return min(2 ** attempts, 60)


async def rate_limit_gate():
    """Self-imposed throttle: stay under 10 requests / rolling 60s before we ever hit 429."""
    if len(_request_times) == 10:
        elapsed = time.time() - _request_times[0]
        if elapsed < 60:
            await asyncio.sleep(60 - elapsed)
    _request_times.append(time.time())


async def fetch_due_jobs(db, limit=10):
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(SendJob)
        .where(SendJob.status == "pending", SendJob.next_attempt_at <= now)
        .limit(limit)
    )
    return result.scalars().all()


async def mark_status(db, job_id, status, dm_id=None):
    values = {"status": status, "updated_at": datetime.now(timezone.utc)}
    if dm_id:
        values["dm_id"] = dm_id
    await db.execute(update(SendJob).where(SendJob.id == job_id).values(**values))
    await db.commit()


async def schedule_retry(db, job, delay=None, count_as_attempt=True):
    new_attempts = job.attempts + (1 if count_as_attempt else 0)
    if count_as_attempt and new_attempts >= MAX_ATTEMPTS:
        await mark_status(db, job.id, "failed")
        return
    delay = delay if delay is not None else backoff_seconds(new_attempts)
    await db.execute(
        update(SendJob)
        .where(SendJob.id == job.id)
        .values(
            status="pending",
            attempts=new_attempts,
            next_attempt_at=datetime.now(timezone.utc) + timedelta(seconds=delay),
            updated_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()


async def send_one(db, job, client: httpx.AsyncClient):
    await mark_status(db, job.id, "sending")
    await rate_limit_gate()
    try:
        resp = await client.post(
            f"{PSEUDOGRAM_BASE_URL}/v1/dm/send",
            headers={"X-API-Key": PSEUDOGRAM_API_KEY, "Idempotency-Key": str(job.id)},
            json={
                "recipient_user_id": job.recipient_user_id,
                "message": job.dm_message,
                "comment_id": job.comment_id,
            },
            timeout=10,
        )
    except httpx.RequestError:
        await schedule_retry(db, job)
        return

    if resp.status_code == 202:
        dm_id = resp.json()["dm_id"]
        await mark_status(db, job.id, "queued", dm_id=dm_id)
    elif resp.status_code == 429:
        retry_after = int(resp.headers.get("Retry-After", 30))
        await schedule_retry(db, job, delay=retry_after, count_as_attempt=False)
    elif resp.status_code == 400:
        await mark_status(db, job.id, "failed")
    else:
        await schedule_retry(db, job)


async def send_worker_loop():
    async with httpx.AsyncClient() as client:
        while True:
            async with AsyncSessionLocal() as db:
                jobs = await fetch_due_jobs(db)
                for job in jobs:
                    await send_one(db, job, client)
            await asyncio.sleep(1)
