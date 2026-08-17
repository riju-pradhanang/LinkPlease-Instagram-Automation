import json
from datetime import datetime

from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Event
from app.services.ingestion import process_event

router = APIRouter()


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    raw_body = await request.body()
    payload = json.loads(raw_body)

    event_id = payload["event_id"]
    event_type = payload["event_type"]
    data = payload.get("data", {})
    from_info = data.get("from", {})

    sent_at = datetime.fromisoformat(
        payload["sent_at"].replace("Z", "+00:00")
    )

    stmt = pg_insert(Event).values(
        event_id=event_id,
        event_type=event_type,
        comment_id=data.get("comment_id"),
        post_id=data.get("post_id"),
        comment_text=data.get("text"),
        from_user_id=from_info.get("user_id"),
        from_username=from_info.get("username"),
        sent_at=sent_at,
        raw_payload=payload,
    ).on_conflict_do_nothing(index_elements=["event_id"])

    result = await db.execute(stmt)
    await db.commit()

    is_new_event = result.rowcount == 1
    if is_new_event:
        background_tasks.add_task(process_event, event_id)

    return {"status": "ok"}