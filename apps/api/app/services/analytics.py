from __future__ import annotations

from collections import defaultdict

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.entities import PlannedWorkout, SetEntry, WorkoutSession, WorkoutSessionExercise


def analytics_summary(db: Session, user_id: str) -> dict:
    planned_count = db.scalar(select(func.count()).select_from(PlannedWorkout).where(PlannedWorkout.user_id == user_id)) or 0
    completed_planned_count = (
        db.scalar(
            select(func.count())
            .select_from(PlannedWorkout)
            .where(PlannedWorkout.user_id == user_id, PlannedWorkout.status == "completed")
        )
        or 0
    )
    total_sessions = db.scalar(select(func.count()).select_from(WorkoutSession).where(WorkoutSession.user_id == user_id)) or 0
    total_completed_sets = db.scalar(
        select(func.count())
        .select_from(SetEntry)
        .join(WorkoutSessionExercise, SetEntry.session_exercise_id == WorkoutSessionExercise.id)
        .join(WorkoutSession, WorkoutSessionExercise.session_id == WorkoutSession.id)
        .where(WorkoutSession.user_id == user_id, SetEntry.completed.is_(True))
    ) or 0
    volume_rows = db.execute(
        select(WorkoutSession.started_at, SetEntry.weight, SetEntry.reps)
        .join(WorkoutSessionExercise, SetEntry.session_exercise_id == WorkoutSessionExercise.id)
        .join(WorkoutSession, WorkoutSessionExercise.session_id == WorkoutSession.id)
        .where(WorkoutSession.user_id == user_id, SetEntry.completed.is_(True))
        .order_by(WorkoutSession.started_at)
    ).all()

    grouped = defaultdict(float)
    total_volume = 0.0
    for started_at, weight, reps in volume_rows:
        entry_volume = float((weight or 0) * (reps or 0))
        total_volume += entry_volume
        if started_at is not None:
            grouped[started_at.date().isoformat()] += entry_volume

    adherence_rate = (completed_planned_count / planned_count) if planned_count else 0.0
    recent_volume = [{"date": key, "volume": value} for key, value in sorted(grouped.items())[-12:]]

    return {
        "adherence_rate": adherence_rate,
        "planned_count": planned_count,
        "completed_planned_count": completed_planned_count,
        "total_sessions": total_sessions,
        "total_completed_sets": total_completed_sets,
        "total_volume": total_volume,
        "recent_volume": recent_volume,
    }

