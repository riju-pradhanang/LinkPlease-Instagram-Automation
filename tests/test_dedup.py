import uuid
import pytest
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.db import AsyncSessionLocal
from app.models import Rule, SendJob


@pytest.mark.asyncio
async def test_duplicate_send_job_is_rejected():
    async with AsyncSessionLocal() as db:
        test_rule = await db.get(Rule, "rule_test")
        if not test_rule:
            db.add(Rule(rule_id="rule_test", keyword="PRICE", dm_message="hi"))
            await db.commit()

        user_id = f"usr_dup_{uuid.uuid4().hex[:8]}"
        stmt = pg_insert(SendJob).values(
            rule_id="rule_test", recipient_user_id=user_id, comment_id="c1", dm_message="hi"
        ).on_conflict_do_nothing(index_elements=["rule_id", "recipient_user_id"])

        first = await db.execute(stmt)
        await db.commit()

        second = await db.execute(stmt)
        await db.commit()

        assert first.rowcount == 1
        assert second.rowcount == 0  # the whole guarantee, in one assertion
