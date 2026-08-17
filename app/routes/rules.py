import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Rule
from app.schemas import RuleCreate, RuleResponse

router = APIRouter()


@router.post("/rules", response_model=RuleResponse, status_code=201)
async def create_rule(payload: RuleCreate, db: AsyncSession = Depends(get_db)):
    rule_id = str(uuid.uuid4())
    rule = Rule(rule_id=rule_id, keyword=payload.keyword, dm_message=payload.dm_message)
    db.add(rule)
    await db.commit()
    return RuleResponse(rule_id=rule_id, keyword=payload.keyword, dm_message=payload.dm_message)