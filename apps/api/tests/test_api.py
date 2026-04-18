from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import (
    BlockWorkout,
    BlockWorkoutExercise,
    Exercise,
    PlannedWorkout,
    ProgressionRule,
    TrainingBlock,
    User,
    WorkoutSession,
    WorkoutSessionExercise,
    SetEntry,
)
from app.services.analytics import analytics_summary
from app.services.planning import generate_planned_workouts


def test_ad_hoc_session_can_exist_without_plan(db_session: Session) -> None:
    user_id = db_session.scalar(select(User.id).where(User.username == "admin"))
    session = WorkoutSession(
        user_id=user_id,
        planned_workout_id=None,
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc) + timedelta(hours=1),
        status="completed",
        title="Hotel gym workout",
        session_notes="Quick session",
    )
    session.exercises.append(
        WorkoutSessionExercise(
            exercise_id=None,
            order_index=0,
            exercise_name_snapshot="Push Up",
            completed=True,
        )
    )
    db_session.add(session)
    db_session.commit()

    stored = db_session.get(WorkoutSession, session.id)
    assert stored is not None
    assert stored.planned_workout_id is None
    assert stored.title == "Hotel gym workout"
    assert stored.exercises[0].exercise_name_snapshot == "Push Up"


def test_block_generation_creates_explicit_planned_workouts(db_session: Session) -> None:
    user_id = db_session.scalar(select(User.id).where(User.username == "admin"))
    exercise_id = db_session.scalar(select(Exercise.id).where(Exercise.name == "Bench Press"))
    exercise = db_session.get(Exercise, exercise_id)

    block = TrainingBlock(user_id=user_id, name="Strength Block", status="draft")
    rule = ProgressionRule(name="Bench Progression", rule_type="fixed_increment", config_json={"weight_increment": 2.5})
    workout = BlockWorkout(name="Upper Day", week_index=1, day_index=2)
    workout.exercises.append(
        BlockWorkoutExercise(
            exercise_id=exercise_id,
            order_index=0,
            target_sets=4,
            target_reps="5",
            target_weight=80,
            exercise=exercise,
            progression_rule=rule,
        )
    )
    block.progression_rules.append(rule)
    block.workouts.append(workout)
    db_session.add(block)
    db_session.commit()

    planned_workouts = generate_planned_workouts(
        db_session,
        training_block=block,
        user_id=user_id,
        start_date=date(2026, 4, 20),
        weeks=3,
    )

    assert len(planned_workouts) == 3
    assert planned_workouts[0].planned_date == date(2026, 4, 21)
    assert planned_workouts[0].exercises[0].exercise_name_snapshot == "Bench Press"
    assert planned_workouts[0].exercises[0].progression_snapshot_json == {"weight_increment": 2.5}


def test_completed_session_updates_analytics(db_session: Session) -> None:
    user_id = db_session.scalar(select(User.id).where(User.username == "admin"))
    exercise_id = db_session.scalar(select(Exercise.id).where(Exercise.name == "Bench Press"))
    planned_workout = PlannedWorkout(
        user_id=user_id,
        planned_date=date(2026, 4, 21),
        status="completed",
        title="Bench Day",
    )
    session = WorkoutSession(
        user_id=user_id,
        planned_workout=planned_workout,
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc),
        status="completed",
        title="Bench Day",
    )
    exercise = WorkoutSessionExercise(
        exercise_id=exercise_id,
        order_index=0,
        exercise_name_snapshot="Bench Press",
        completed=True,
    )
    exercise.set_entries.append(
        SetEntry(
            set_number=1,
            completed=True,
            reps=5,
            weight=82.5,
        )
    )
    session.exercises.append(exercise)
    db_session.add_all([planned_workout, session])
    db_session.commit()

    summary = analytics_summary(db_session, user_id)
    assert summary["completed_planned_count"] == 1
    assert summary["total_sessions"] == 1
    assert summary["total_completed_sets"] == 1
    assert summary["total_volume"] == 412.5
