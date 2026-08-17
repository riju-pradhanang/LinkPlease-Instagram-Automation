from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Rule
from app.schemas import RuleCreate, RuleResponse

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(rule_in: RuleCreate, db: Session = Depends(get_db)):
    rule = Rule(keyword=rule_in.keyword.lower().strip(), response_link=rule_in.response_link)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
