from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import ExerciseLineBase, ORMModel, SetEntryPayload


class LoginPayload(BaseModel):
    username: str
    password: str


class AuthUser(ORMModel):
    id: str
    username: str


class ExerciseCreate(BaseModel):
    name: str
    modality: str = "strength"
    default_measure_type: str = "reps_weight"
    notes: str | None = None


class ExerciseRead(ORMModel):
    id: str
    name: str
    modality: str
    default_measure_type: str
    notes: str | None = None
    archived_at: datetime | None = None


class WorkoutTemplateExercisePayload(ExerciseLineBase):
    pass


class WorkoutTemplateCreate(BaseModel):
    name: str
    description: str | None = None
    exercises: list[WorkoutTemplateExercisePayload] = Field(default_factory=list)


class WorkoutTemplateRead(ORMModel):
    id: str
    name: str
    description: str | None = None
    exercises: list[dict]


class ProgressionRulePayload(BaseModel):
    id: str | None = None
    name: str
    rule_type: str = "fixed_increment"
    config_json: dict | None = None
    deload_strategy: str | None = None
    notes: str | None = None


class BlockWorkoutExercisePayload(ExerciseLineBase):
    progression_rule_id: str | None = None


class BlockWorkoutPayload(BaseModel):
    id: str | None = None
    name: str
    week_index: int = 1
    day_index: int = 1
    notes: str | None = None
    exercises: list[BlockWorkoutExercisePayload] = Field(default_factory=list)


class TrainingBlockCreate(BaseModel):
    name: str
    goal: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = "draft"
    progression_rules: list[ProgressionRulePayload] = Field(default_factory=list)
    workouts: list[BlockWorkoutPayload] = Field(default_factory=list)


class PlannedWorkoutExercisePayload(ExerciseLineBase):
    progression_rule_id: str | None = None
    exercise_name_snapshot: str | None = None
    progression_snapshot_json: dict | None = None


class PlannedWorkoutCreate(BaseModel):
    planned_date: date
    planned_start_time: datetime | None = None
    status: str = "planned"
    title: str
    notes: str | None = None
    training_block_id: str | None = None
    block_workout_id: str | None = None
    workout_template_id: str | None = None
    exercises: list[PlannedWorkoutExercisePayload] = Field(default_factory=list)


class GeneratePlannedWorkoutsPayload(BaseModel):
    start_date: date
    weeks: int = 4


class WorkoutSessionExercisePayload(BaseModel):
    id: str | None = None
    exercise_id: str | None = None
    planned_workout_exercise_id: str | None = None
    order_index: int = 0
    exercise_name_snapshot: str
    notes: str | None = None
    target_sets: int | None = None
    target_reps: str | None = None
    target_weight: float | None = None
    target_duration_seconds: int | None = None
    target_distance_meters: int | None = None
    target_rpe: float | None = None
    completed: bool = False
    set_entries: list[SetEntryPayload] = Field(default_factory=list)


class WorkoutSessionCreate(BaseModel):
    planned_workout_id: str | None = None
    started_at: datetime
    ended_at: datetime | None = None
    status: str = "in_progress"
    title: str
    session_notes: str | None = None
    exercises: list[WorkoutSessionExercisePayload] = Field(default_factory=list)


class AnalyticsResponse(BaseModel):
    adherence_rate: float
    planned_count: int
    completed_planned_count: int
    total_sessions: int
    total_completed_sets: int
    total_volume: float
    recent_volume: list[dict]
