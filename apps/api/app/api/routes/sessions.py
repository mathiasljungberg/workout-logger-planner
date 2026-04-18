from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import PlannedWorkout, SetEntry, User, WorkoutSession, WorkoutSessionExercise
from app.schemas.domain import WorkoutSessionCreate

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _serialize_session(item: WorkoutSession) -> dict:
    return {
        "id": item.id,
        "planned_workout_id": item.planned_workout_id,
        "started_at": item.started_at,
        "ended_at": item.ended_at,
        "status": item.status,
        "title": item.title,
        "session_notes": item.session_notes,
        "exercises": [
            {
                "id": exercise.id,
                "exercise_id": exercise.exercise_id,
                "planned_workout_exercise_id": exercise.planned_workout_exercise_id,
                "order_index": exercise.order_index,
                "exercise_name_snapshot": exercise.exercise_name_snapshot,
                "notes": exercise.notes,
                "target_sets": exercise.target_sets,
                "target_reps": exercise.target_reps,
                "target_weight": exercise.target_weight,
                "target_duration_seconds": exercise.target_duration_seconds,
                "target_distance_meters": exercise.target_distance_meters,
                "target_rpe": exercise.target_rpe,
                "completed": exercise.completed,
                "set_entries": [
                    {
                        "id": set_entry.id,
                        "set_number": set_entry.set_number,
                        "set_type": set_entry.set_type,
                        "completed": set_entry.completed,
                        "reps": set_entry.reps,
                        "weight": set_entry.weight,
                        "duration_seconds": set_entry.duration_seconds,
                        "distance_meters": set_entry.distance_meters,
                        "rpe": set_entry.rpe,
                        "rest_seconds": set_entry.rest_seconds,
                        "comment": set_entry.comment,
                    }
                    for set_entry in exercise.set_entries
                ],
            }
            for exercise in item.exercises
        ],
    }


def _apply_session_payload(item: WorkoutSession, payload: WorkoutSessionCreate) -> None:
    item.planned_workout_id = payload.planned_workout_id
    item.started_at = payload.started_at
    item.ended_at = payload.ended_at
    item.status = payload.status
    item.title = payload.title
    item.session_notes = payload.session_notes
    item.exercises.clear()
    for exercise_payload in payload.exercises:
        session_exercise = WorkoutSessionExercise(
            exercise_id=exercise_payload.exercise_id,
            planned_workout_exercise_id=exercise_payload.planned_workout_exercise_id,
            order_index=exercise_payload.order_index,
            exercise_name_snapshot=exercise_payload.exercise_name_snapshot,
            notes=exercise_payload.notes,
            target_sets=exercise_payload.target_sets,
            target_reps=exercise_payload.target_reps,
            target_weight=exercise_payload.target_weight,
            target_duration_seconds=exercise_payload.target_duration_seconds,
            target_distance_meters=exercise_payload.target_distance_meters,
            target_rpe=exercise_payload.target_rpe,
            completed=exercise_payload.completed,
        )
        for set_payload in exercise_payload.set_entries:
            session_exercise.set_entries.append(SetEntry(**set_payload.model_dump(exclude={"id"})))
        item.exercises.append(session_exercise)


@router.get("/{session_id}")
def get_session(session_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    item = db.scalar(
        select(WorkoutSession)
        .options(selectinload(WorkoutSession.exercises).selectinload(WorkoutSessionExercise.set_entries))
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == user.id)
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return _serialize_session(item)


@router.get("")
def list_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    items = db.scalars(
        select(WorkoutSession)
        .options(selectinload(WorkoutSession.exercises).selectinload(WorkoutSessionExercise.set_entries))
        .where(WorkoutSession.user_id == user.id)
        .order_by(WorkoutSession.started_at.desc())
    ).all()
    return [_serialize_session(item) for item in items]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_session(
    payload: WorkoutSessionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if payload.planned_workout_id:
        planned_workout = db.scalar(
            select(PlannedWorkout)
            .options(selectinload(PlannedWorkout.exercises))
            .where(PlannedWorkout.id == payload.planned_workout_id, PlannedWorkout.user_id == user.id)
        )
        if planned_workout is None:
            raise HTTPException(status_code=404, detail="Planned workout not found")
    item = WorkoutSession(user_id=user.id, started_at=payload.started_at, title=payload.title)
    _apply_session_payload(item, payload)
    db.add(item)
    if payload.planned_workout_id:
        planned_workout = db.get(PlannedWorkout, payload.planned_workout_id)
        if planned_workout is not None and item.status == "completed":
            planned_workout.status = "completed"
    db.commit()
    item = db.scalar(
        select(WorkoutSession)
        .options(selectinload(WorkoutSession.exercises).selectinload(WorkoutSessionExercise.set_entries))
        .where(WorkoutSession.id == item.id)
    )
    return _serialize_session(item)


@router.patch("/{session_id}")
def update_session(
    session_id: str,
    payload: WorkoutSessionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    item = db.scalar(
        select(WorkoutSession)
        .options(selectinload(WorkoutSession.exercises).selectinload(WorkoutSessionExercise.set_entries))
        .where(WorkoutSession.id == session_id, WorkoutSession.user_id == user.id)
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Session not found")
    _apply_session_payload(item, payload)
    if payload.planned_workout_id:
        planned_workout = db.get(PlannedWorkout, payload.planned_workout_id)
        if planned_workout is not None and item.status == "completed":
            planned_workout.status = "completed"
    db.commit()
    item = db.scalar(
        select(WorkoutSession)
        .options(selectinload(WorkoutSession.exercises).selectinload(WorkoutSessionExercise.set_entries))
        .where(WorkoutSession.id == session_id)
    )
    return _serialize_session(item)

