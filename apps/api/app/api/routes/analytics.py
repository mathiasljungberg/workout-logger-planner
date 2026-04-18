from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.domain import AnalyticsResponse
from app.services.analytics import analytics_summary

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsResponse)
def summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return analytics_summary(db, user.id)

