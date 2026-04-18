from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import (
    BlockWorkout,
    BlockWorkoutExercise,
    ProgressionRule,
    TrainingBlock,
    User,
)
from app.schemas.domain import GeneratePlannedWorkoutsPayload, TrainingBlockCreate
from app.services.planning import generate_planned_workouts

router = APIRouter(prefix="/blocks", tags=["blocks"])


def _serialize_block(block: TrainingBlock) -> dict:
    return {
        "id": block.id,
        "name": block.name,
        "goal": block.goal,
        "start_date": block.start_date,
        "end_date": block.end_date,
        "status": block.status,
        "progression_rules": [
            {
                "id": rule.id,
                "name": rule.name,
                "rule_type": rule.rule_type,
                "config_json": rule.config_json,
                "deload_strategy": rule.deload_strategy,
                "notes": rule.notes,
            }
            for rule in block.progression_rules
        ],
        "workouts": [
            {
                "id": workout.id,
                "name": workout.name,
                "week_index": workout.week_index,
                "day_index": workout.day_index,
                "notes": workout.notes,
                "exercises": [
                    {
                        "id": exercise.id,
                        "exercise_id": exercise.exercise_id,
                        "exercise_name": exercise.exercise.name,
                        "progression_rule_id": exercise.progression_rule_id,
                        "order_index": exercise.order_index,
                        "notes": exercise.notes,
                        "target_sets": exercise.target_sets,
                        "target_reps": exercise.target_reps,
                        "target_weight": exercise.target_weight,
                        "target_duration_seconds": exercise.target_duration_seconds,
                        "target_distance_meters": exercise.target_distance_meters,
                        "target_rpe": exercise.target_rpe,
                    }
                    for exercise in workout.exercises
                ],
            }
            for workout in block.workouts
        ],
    }


def _apply_block_payload(block: TrainingBlock, payload: TrainingBlockCreate) -> None:
    block.name = payload.name
    block.goal = payload.goal
    block.start_date = payload.start_date
    block.end_date = payload.end_date
    block.status = payload.status
    block.progression_rules.clear()
    block.workouts.clear()
    for rule in payload.progression_rules:
        block.progression_rules.append(ProgressionRule(**rule.model_dump(exclude={"id"})))
    for workout_payload in payload.workouts:
        workout = BlockWorkout(
            name=workout_payload.name,
            week_index=workout_payload.week_index,
            day_index=workout_payload.day_index,
            notes=workout_payload.notes,
        )
        for item in workout_payload.exercises:
            workout.exercises.append(BlockWorkoutExercise(**item.model_dump()))
        block.workouts.append(workout)


@router.get("")
def list_blocks(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict]:
    blocks = db.scalars(
        select(TrainingBlock)
        .options(
            selectinload(TrainingBlock.progression_rules),
            selectinload(TrainingBlock.workouts)
            .selectinload(BlockWorkout.exercises)
            .selectinload(BlockWorkoutExercise.exercise),
        )
        .where(TrainingBlock.user_id == user.id)
        .order_by(TrainingBlock.created_at.desc())
    ).all()
    return [_serialize_block(block) for block in blocks]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_block(
    payload: TrainingBlockCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    block = TrainingBlock(user_id=user.id, name=payload.name, goal=payload.goal)
    _apply_block_payload(block, payload)
    db.add(block)
    db.commit()
    block = db.scalar(
        select(TrainingBlock)
        .options(
            selectinload(TrainingBlock.progression_rules),
            selectinload(TrainingBlock.workouts)
            .selectinload(BlockWorkout.exercises)
            .selectinload(BlockWorkoutExercise.exercise),
        )
        .where(TrainingBlock.id == block.id)
    )
    return _serialize_block(block)


@router.patch("/{block_id}")
def update_block(
    block_id: str,
    payload: TrainingBlockCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    block = db.scalar(
        select(TrainingBlock)
        .options(
            selectinload(TrainingBlock.progression_rules),
            selectinload(TrainingBlock.workouts).selectinload(BlockWorkout.exercises),
        )
        .where(TrainingBlock.id == block_id, TrainingBlock.user_id == user.id)
    )
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    _apply_block_payload(block, payload)
    db.commit()
    block = db.scalar(
        select(TrainingBlock)
        .options(
            selectinload(TrainingBlock.progression_rules),
            selectinload(TrainingBlock.workouts)
            .selectinload(BlockWorkout.exercises)
            .selectinload(BlockWorkoutExercise.exercise),
        )
        .where(TrainingBlock.id == block_id)
    )
    return _serialize_block(block)


@router.post("/{block_id}/generate-planned-workouts")
def generate_block_plan(
    block_id: str,
    payload: GeneratePlannedWorkoutsPayload,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    block = db.scalar(
        select(TrainingBlock)
        .options(
            selectinload(TrainingBlock.workouts)
            .selectinload(BlockWorkout.exercises)
            .selectinload(BlockWorkoutExercise.exercise),
            selectinload(TrainingBlock.workouts)
            .selectinload(BlockWorkout.exercises)
            .selectinload(BlockWorkoutExercise.progression_rule),
        )
        .where(TrainingBlock.id == block_id, TrainingBlock.user_id == user.id)
    )
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    planned_workouts = generate_planned_workouts(
        db,
        training_block=block,
        user_id=user.id,
        start_date=payload.start_date,
        weeks=payload.weeks,
    )
    return [{"id": planned.id, "planned_date": planned.planned_date, "title": planned.title} for planned in planned_workouts]

