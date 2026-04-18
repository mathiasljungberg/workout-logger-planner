from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import User, WorkoutTemplate, WorkoutTemplateExercise
from app.schemas.domain import WorkoutTemplateCreate

router = APIRouter(prefix="/templates", tags=["templates"])


def _serialize_template(template: WorkoutTemplate) -> dict:
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "exercises": [
            {
                "id": exercise.id,
                "exercise_id": exercise.exercise_id,
                "exercise_name": exercise.exercise.name,
                "order_index": exercise.order_index,
                "notes": exercise.notes,
                "target_sets": exercise.target_sets,
                "target_reps": exercise.target_reps,
                "target_weight": exercise.target_weight,
                "target_duration_seconds": exercise.target_duration_seconds,
                "target_distance_meters": exercise.target_distance_meters,
                "target_rpe": exercise.target_rpe,
            }
            for exercise in template.exercises
        ],
    }


def _apply_template_payload(template: WorkoutTemplate, payload: WorkoutTemplateCreate) -> None:
    template.name = payload.name
    template.description = payload.description
    template.exercises.clear()
    for item in payload.exercises:
        template.exercises.append(WorkoutTemplateExercise(**item.model_dump()))


@router.get("")
def list_templates(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    templates = db.scalars(
        select(WorkoutTemplate)
        .options(selectinload(WorkoutTemplate.exercises).selectinload(WorkoutTemplateExercise.exercise))
        .where(WorkoutTemplate.user_id == user.id)
        .order_by(WorkoutTemplate.name)
    ).all()
    return [_serialize_template(template) for template in templates]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_template(
    payload: WorkoutTemplateCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    template = WorkoutTemplate(user_id=user.id, name=payload.name, description=payload.description)
    _apply_template_payload(template, payload)
    db.add(template)
    db.commit()
    db.refresh(template)
    return _serialize_template(
        db.scalar(
            select(WorkoutTemplate)
            .options(selectinload(WorkoutTemplate.exercises).selectinload(WorkoutTemplateExercise.exercise))
            .where(WorkoutTemplate.id == template.id)
        )
    )


@router.patch("/{template_id}")
def update_template(
    template_id: str,
    payload: WorkoutTemplateCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    template = db.scalar(
        select(WorkoutTemplate)
        .options(selectinload(WorkoutTemplate.exercises))
        .where(WorkoutTemplate.id == template_id, WorkoutTemplate.user_id == user.id)
    )
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    _apply_template_payload(template, payload)
    db.commit()
    template = db.scalar(
        select(WorkoutTemplate)
        .options(selectinload(WorkoutTemplate.exercises).selectinload(WorkoutTemplateExercise.exercise))
        .where(WorkoutTemplate.id == template_id)
    )
    return _serialize_template(template)

