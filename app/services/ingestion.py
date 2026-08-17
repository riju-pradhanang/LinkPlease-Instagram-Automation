from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.db import AsyncSessionLocal
from app.models import Event, Rule, SendJob, StatsCounter


async def process_event(event_id: str):
    async with AsyncSessionLocal() as db:
        event = await db.get(Event, event_id)
        if event is None:
            return
        if event.event_type != "comment.created":
            return
        if not event.comment_text or not event.from_user_id:
            return

        result = await db.execute(select(Rule))
        rules = result.scalars().all()

        text_lower = event.comment_text.lower()

        for rule in rules:
            if rule.keyword.lower() in text_lower:
                stmt = pg_insert(SendJob).values(
                    rule_id=rule.rule_id,
                    recipient_user_id=event.from_user_id,
                    comment_id=event.comment_id,
                    dm_message=rule.dm_message,
                ).on_conflict_do_nothing(index_elements=["rule_id", "recipient_user_id"])

                res = await db.execute(stmt)
                if res.rowcount == 0:
                    await db.execute(
                        update(StatsCounter).values(
                            duplicates_blocked=StatsCounter.duplicates_blocked + 1
                        )
                    )
                await db.commit()