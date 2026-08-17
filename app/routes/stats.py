from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import SendJob, StatsCounter
from app.schemas import StatsResponse

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            func.count().filter(SendJob.status == "delivered"),
            func.count().filter(SendJob.status == "failed"),
            func.count().filter(SendJob.status.in_(["pending", "sending", "queued"])),
        )
    )
    sent, failed, queued = result.one()
    counter = (await db.execute(select(StatsCounter))).scalars().first()
    duplicates_blocked = counter.duplicates_blocked if counter else 0
    return StatsResponse(sent=sent, failed=failed, queued=queued, duplicates_blocked=duplicates_blocked)
