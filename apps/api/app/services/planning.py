from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.entities import BlockWorkout, PlannedWorkout, PlannedWorkoutExercise, TrainingBlock


def build_planned_workout_from_block_workout(
    *,
    training_block: TrainingBlock,
    block_workout: BlockWorkout,
    planned_date,
    user_id: str,
) -> PlannedWorkout:
    planned = PlannedWorkout(
        user_id=user_id,
        planned_date=planned_date,
        title=block_workout.name,
        notes=block_workout.notes,
        training_block_id=training_block.id,
        block_workout_id=block_workout.id,
        status="planned",
    )
    for exercise in block_workout.exercises:
        planned.exercises.append(
            PlannedWorkoutExercise(
                exercise_id=exercise.exercise_id,
                progression_rule_id=exercise.progression_rule_id,
                order_index=exercise.order_index,
                exercise_name_snapshot=exercise.exercise.name,
                notes=exercise.notes,
                target_sets=exercise.target_sets,
                target_reps=exercise.target_reps,
                target_weight=exercise.target_weight,
                target_duration_seconds=exercise.target_duration_seconds,
                target_distance_meters=exercise.target_distance_meters,
                target_rpe=exercise.target_rpe,
                progression_snapshot_json=exercise.progression_rule.config_json if exercise.progression_rule else {},
            )
        )
    return planned


def generate_planned_workouts(
    db: Session,
    *,
    training_block: TrainingBlock,
    user_id: str,
    start_date,
    weeks: int,
) -> list[PlannedWorkout]:
    planned_workouts: list[PlannedWorkout] = []
    for block_workout in training_block.workouts:
        for week_offset in range(weeks):
            planned_date = start_date + timedelta(days=((week_offset * 7) + (block_workout.day_index - 1)))
            planned = build_planned_workout_from_block_workout(
                training_block=training_block,
                block_workout=block_workout,
                planned_date=planned_date,
                user_id=user_id,
            )
            db.add(planned)
            planned_workouts.append(planned)
    db.commit()
    for planned in planned_workouts:
        db.refresh(planned)
    return planned_workouts

