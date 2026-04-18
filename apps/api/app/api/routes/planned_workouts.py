from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import Exercise, PlannedWorkout, PlannedWorkoutExercise, User
from app.schemas.domain import PlannedWorkoutCreate

router = APIRouter(prefix="/planned-workouts", tags=["planned-workouts"])


def _serialize_planned_workout(item: PlannedWorkout) -> dict:
    return {
        "id": item.id,
        "planned_date": item.planned_date,
        "planned_start_time": item.planned_start_time,
        "status": item.status,
        "title": item.title,
        "notes": item.notes,
        "training_block_id": item.training_block_id,
        "block_workout_id": item.block_workout_id,
        "workout_template_id": item.workout_template_id,
        "session_id": item.session.id if item.session else None,
        "exercises": [
            {
                "id": exercise.id,
                "exercise_id": exercise.exercise_id,
                "exercise_name_snapshot": exercise.exercise_name_snapshot,
                "progression_rule_id": exercise.progression_rule_id,
                "order_index": exercise.order_index,
                "notes": exercise.notes,
                "target_sets": exercise.target_sets,
                "target_reps": exercise.target_reps,
                "target_weight": exercise.target_weight,
                "target_duration_seconds": exercise.target_duration_seconds,
                "target_distance_meters": exercise.target_distance_meters,
                "target_rpe": exercise.target_rpe,
                "progression_snapshot_json": exercise.progression_snapshot_json,
            }
            for exercise in item.exercises
        ],
    }


def _apply_planned_workout_payload(db: Session, planned_workout: PlannedWorkout, payload: PlannedWorkoutCreate) -> None:
    planned_workout.planned_date = payload.planned_date
    planned_workout.planned_start_time = payload.planned_start_time
    planned_workout.status = payload.status
    planned_workout.title = payload.title
    planned_workout.notes = payload.notes
    planned_workout.training_block_id = payload.training_block_id
    planned_workout.block_workout_id = payload.block_workout_id
    planned_workout.workout_template_id = payload.workout_template_id
    planned_workout.exercises.clear()
    for item in payload.exercises:
        exercise = db.get(Exercise, item.exercise_id)
        exercise_name = item.exercise_name_snapshot or (exercise.name if exercise else "Unknown Exercise")
        planned_workout.exercises.append(
            PlannedWorkoutExercise(
                **item.model_dump(exclude={"exercise_name_snapshot"}),
                exercise_name_snapshot=exercise_name,
            )
        )


@router.get("")
def list_planned_workouts(
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    query = (
        select(PlannedWorkout)
        .options(
            selectinload(PlannedWorkout.exercises),
            selectinload(PlannedWorkout.session),
        )
        .where(PlannedWorkout.user_id == user.id)
        .order_by(PlannedWorkout.planned_date)
    )
    if start:
        query = query.where(PlannedWorkout.planned_date >= date.fromisoformat(start))
    if end:
        query = query.where(PlannedWorkout.planned_date <= date.fromisoformat(end))
    return [_serialize_planned_workout(item) for item in db.scalars(query).all()]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_planned_workout(
    payload: PlannedWorkoutCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    planned_workout = PlannedWorkout(user_id=user.id, planned_date=payload.planned_date, title=payload.title)
    _apply_planned_workout_payload(db, planned_workout, payload)
    db.add(planned_workout)
    db.commit()
    planned_workout = db.scalar(
        select(PlannedWorkout)
        .options(selectinload(PlannedWorkout.exercises), selectinload(PlannedWorkout.session))
        .where(PlannedWorkout.id == planned_workout.id)
    )
    return _serialize_planned_workout(planned_workout)


@router.patch("/{planned_workout_id}")
def update_planned_workout(
    planned_workout_id: str,
    payload: PlannedWorkoutCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    planned_workout = db.scalar(
        select(PlannedWorkout)
        .options(selectinload(PlannedWorkout.exercises))
        .where(PlannedWorkout.id == planned_workout_id, PlannedWorkout.user_id == user.id)
    )
    if planned_workout is None:
        raise HTTPException(status_code=404, detail="Planned workout not found")
    _apply_planned_workout_payload(db, planned_workout, payload)
    db.commit()
    planned_workout = db.scalar(
        select(PlannedWorkout)
        .options(selectinload(PlannedWorkout.exercises), selectinload(PlannedWorkout.session))
        .where(PlannedWorkout.id == planned_workout_id)
    )
    return _serialize_planned_workout(planned_workout)
