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
from app.schemas.domain import (
    BlockWorkoutExerciseRead,
    BlockWorkoutRead,
    GeneratePlannedWorkoutsPayload,
    GeneratedPlannedWorkoutRead,
    ProgressionRuleRead,
    TrainingBlockCreate,
    TrainingBlockDetail,
)
from app.services.planning import generate_planned_workouts
from app.services.progression import propagate_block_progressions

router = APIRouter(prefix="/blocks", tags=["blocks"])


def _serialize_block(block: TrainingBlock) -> TrainingBlockDetail:
    return TrainingBlockDetail(
        id=block.id,
        name=block.name,
        goal=block.goal,
        start_date=block.start_date,
        end_date=block.end_date,
        status=block.status,
        progression_rules=[
            ProgressionRuleRead.model_validate(rule) for rule in block.progression_rules
        ],
        workouts=[
            BlockWorkoutRead(
                id=workout.id,
                name=workout.name,
                week_index=workout.week_index,
                day_index=workout.day_index,
                notes=workout.notes,
                exercises=[
                    BlockWorkoutExerciseRead(
                        id=exercise.id,
                        exercise_id=exercise.exercise_id,
                        exercise_name=exercise.exercise.name,
                        progression_rule_id=exercise.progression_rule_id,
                        order_index=exercise.order_index,
                        notes=exercise.notes,
                        target_sets=exercise.target_sets,
                        target_reps=exercise.target_reps,
                        target_weight=exercise.target_weight,
                        target_duration_seconds=exercise.target_duration_seconds,
                        target_distance_meters=exercise.target_distance_meters,
                        target_rpe=exercise.target_rpe,
                        manual_override=exercise.manual_override,
                        progression_snapshot_json=exercise.progression_snapshot_json,
                    )
                    for exercise in workout.exercises
                ],
            )
            for workout in block.workouts
        ],
    )


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


def _load_block(db: Session, block_id: str, user_id: str) -> TrainingBlock | None:
    return db.scalar(
        select(TrainingBlock)
        .options(
            selectinload(TrainingBlock.progression_rules),
            selectinload(TrainingBlock.workouts)
            .selectinload(BlockWorkout.exercises)
            .selectinload(BlockWorkoutExercise.exercise),
        )
        .where(TrainingBlock.id == block_id, TrainingBlock.user_id == user_id)
    )


@router.get("", response_model=list[TrainingBlockDetail])
def list_blocks(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[TrainingBlockDetail]:
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


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TrainingBlockDetail)
def create_block(
    payload: TrainingBlockCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrainingBlockDetail:
    block = TrainingBlock(user_id=user.id, name=payload.name, goal=payload.goal)
    _apply_block_payload(block, payload)
    db.add(block)
    db.commit()
    propagate_block_progressions(db, block.id)
    block = _load_block(db, block.id, user.id)
    return _serialize_block(block)


@router.patch("/{block_id}", response_model=TrainingBlockDetail)
def update_block(
    block_id: str,
    payload: TrainingBlockCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrainingBlockDetail:
    block = _load_block(db, block_id, user.id)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    _apply_block_payload(block, payload)
    db.commit()
    propagate_block_progressions(db, block.id)
    block = _load_block(db, block_id, user.id)
    return _serialize_block(block)


@router.post("/{block_id}/propagate-progressions", response_model=TrainingBlockDetail)
def propagate_progressions(
    block_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrainingBlockDetail:
    block = _load_block(db, block_id, user.id)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    propagate_block_progressions(db, block_id)
    block = _load_block(db, block_id, user.id)
    return _serialize_block(block)


@router.post("/{block_id}/generate-planned-workouts", response_model=list[GeneratedPlannedWorkoutRead])
def generate_block_plan(
    block_id: str,
    payload: GeneratePlannedWorkoutsPayload,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[GeneratedPlannedWorkoutRead]:
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
    return [
        GeneratedPlannedWorkoutRead(id=p.id, planned_date=p.planned_date, title=p.title)
        for p in planned_workouts
    ]
