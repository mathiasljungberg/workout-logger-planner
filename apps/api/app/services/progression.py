from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import (
    BlockWorkout,
    BlockWorkoutExercise,
    ProgressionRule,
    RuleType,
    TrainingBlock,
)


def propagate_block_progressions(db: Session, block_id: str) -> None:
    """Fill in later-week target_weight values from a lowest-week anchor row.

    For each (day_index, order_index, exercise_id) slot, the lowest-week row with
    a progression_rule set is the anchor. Higher-week rows in the same slot that
    are not manually overridden get target_weight = base + (week - anchor_week) * increment
    when the rule is fixed_increment. Manual-typed rules and rules with no
    increment are no-ops.
    """
    block = db.scalar(
        select(TrainingBlock)
        .options(
            selectinload(TrainingBlock.workouts)
            .selectinload(BlockWorkout.exercises)
            .selectinload(BlockWorkoutExercise.progression_rule),
        )
        .where(TrainingBlock.id == block_id)
    )
    if block is None:
        return

    slots: dict[tuple[int, int, str], list[tuple[BlockWorkout, BlockWorkoutExercise]]] = defaultdict(list)
    for workout in block.workouts:
        for bwe in workout.exercises:
            key = (workout.day_index, bwe.order_index, bwe.exercise_id)
            slots[key].append((workout, bwe))

    for rows in slots.values():
        rows.sort(key=lambda pair: pair[0].week_index)
        anchor_idx = next(
            (i for i, (_, bwe) in enumerate(rows) if bwe.progression_rule is not None),
            None,
        )
        if anchor_idx is None:
            continue
        anchor_workout, anchor_bwe = rows[anchor_idx]
        rule = anchor_bwe.progression_rule
        if rule.rule_type != RuleType.FIXED_INCREMENT.value:
            continue
        increment = _read_increment(rule)
        if increment is None or anchor_bwe.target_weight is None:
            continue
        base_weight = anchor_bwe.target_weight
        anchor_week = anchor_workout.week_index
        for workout, bwe in rows[anchor_idx + 1 :]:
            if bwe.manual_override:
                continue
            bwe.target_weight = base_weight + (workout.week_index - anchor_week) * increment
            if bwe.progression_rule_id is None:
                bwe.progression_rule_id = rule.id
            bwe.progression_snapshot_json = {
                "source": "fixed_increment_weekly",
                "anchor_week": anchor_week,
                "base_weight": base_weight,
                "increment": increment,
                "computed_week": workout.week_index,
            }

    db.commit()


def _read_increment(rule: ProgressionRule) -> float | None:
    config = rule.config_json or {}
    value = config.get("weight_increment")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
