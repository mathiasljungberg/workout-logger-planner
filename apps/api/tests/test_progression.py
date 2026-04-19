from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import (
    BlockWorkout,
    BlockWorkoutExercise,
    Exercise,
    ProgressionRule,
    TrainingBlock,
    User,
)
from app.services.progression import propagate_block_progressions


def _build_block(
    db: Session,
    *,
    weeks: int,
    anchor_weight: float,
    increment: float | None,
    rule_type: str = "fixed_increment",
) -> tuple[str, ProgressionRule, list[BlockWorkoutExercise]]:
    user_id = db.scalar(select(User.id).where(User.username == "admin"))
    exercise_id = db.scalar(select(Exercise.id).where(Exercise.name == "Bench Press"))
    exercise = db.get(Exercise, exercise_id)

    block = TrainingBlock(user_id=user_id, name="Block", status="draft")
    rule = ProgressionRule(
        name="Bench Progression",
        rule_type=rule_type,
        config_json={"weight_increment": increment} if increment is not None else {},
    )
    block.progression_rules.append(rule)

    rows: list[BlockWorkoutExercise] = []
    for week_index in range(1, weeks + 1):
        workout = BlockWorkout(name="Upper Day", week_index=week_index, day_index=2)
        row = BlockWorkoutExercise(
            exercise_id=exercise_id,
            order_index=0,
            target_sets=4,
            target_reps="5",
            target_weight=anchor_weight if week_index == 1 else None,
            exercise=exercise,
            progression_rule=rule,
        )
        workout.exercises.append(row)
        block.workouts.append(workout)
        rows.append(row)

    db.add(block)
    db.commit()
    return block.id, rule, rows


def test_propagate_fills_later_weeks_from_anchor(db_session: Session) -> None:
    block_id, _, rows = _build_block(db_session, weeks=4, anchor_weight=60.0, increment=2.5)

    propagate_block_progressions(db_session, block_id)

    db_session.refresh(rows[0])
    db_session.refresh(rows[1])
    db_session.refresh(rows[2])
    db_session.refresh(rows[3])
    assert rows[0].target_weight == 60.0
    assert rows[1].target_weight == 62.5
    assert rows[2].target_weight == 65.0
    assert rows[3].target_weight == 67.5
    assert rows[1].progression_snapshot_json["source"] == "fixed_increment_weekly"
    assert rows[1].progression_snapshot_json["anchor_week"] == 1
    assert rows[1].progression_snapshot_json["base_weight"] == 60.0
    assert rows[1].progression_snapshot_json["increment"] == 2.5
    assert rows[1].progression_snapshot_json["computed_week"] == 2


def test_manual_override_is_preserved(db_session: Session) -> None:
    block_id, _, rows = _build_block(db_session, weeks=4, anchor_weight=60.0, increment=2.5)

    rows[2].target_weight = 70.0
    rows[2].manual_override = True
    db_session.commit()

    propagate_block_progressions(db_session, block_id)

    for row in rows:
        db_session.refresh(row)
    assert rows[0].target_weight == 60.0
    assert rows[1].target_weight == 62.5
    assert rows[2].target_weight == 70.0
    assert rows[3].target_weight == 67.5


def test_manual_rule_is_no_op(db_session: Session) -> None:
    block_id, _, rows = _build_block(
        db_session, weeks=3, anchor_weight=60.0, increment=2.5, rule_type="manual"
    )

    propagate_block_progressions(db_session, block_id)

    for row in rows:
        db_session.refresh(row)
    assert rows[0].target_weight == 60.0
    assert rows[1].target_weight is None
    assert rows[2].target_weight is None


def test_no_increment_in_config_is_no_op(db_session: Session) -> None:
    block_id, _, rows = _build_block(db_session, weeks=3, anchor_weight=60.0, increment=None)

    propagate_block_progressions(db_session, block_id)

    for row in rows:
        db_session.refresh(row)
    assert rows[0].target_weight == 60.0
    assert rows[1].target_weight is None
    assert rows[2].target_weight is None


def test_propagate_runs_at_block_creation(db_session: Session) -> None:
    block_id, _, rows = _build_block(db_session, weeks=3, anchor_weight=80.0, increment=5.0)

    propagate_block_progressions(db_session, block_id)

    for row in rows:
        db_session.refresh(row)
    assert rows[0].target_weight == 80.0
    assert rows[1].target_weight == 85.0
    assert rows[2].target_weight == 90.0
