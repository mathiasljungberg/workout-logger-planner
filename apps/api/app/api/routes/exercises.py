from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import Exercise, User
from app.schemas.domain import ExerciseCreate, ExerciseRead

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseRead])
def list_exercises(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Exercise]:
    return list(db.scalars(select(Exercise).order_by(Exercise.name)).all())


@router.post("", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
def create_exercise(payload: ExerciseCreate, _: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Exercise:
    exercise = Exercise(**payload.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.patch("/{exercise_id}", response_model=ExerciseRead)
def update_exercise(
    exercise_id: str,
    payload: ExerciseCreate,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Exercise:
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    for key, value in payload.model_dump().items():
        setattr(exercise, key, value)
    db.commit()
    db.refresh(exercise)
    return exercise

