from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ExerciseLineBase(BaseModel):
    exercise_id: str
    order_index: int = 0
    notes: str | None = None
    target_sets: int | None = None
    target_reps: str | None = None
    target_weight: float | None = None
    target_duration_seconds: int | None = None
    target_distance_meters: int | None = None
    target_rpe: float | None = None


class SetEntryPayload(BaseModel):
    id: str | None = None
    set_number: int
    set_type: str = "work"
    completed: bool = False
    reps: int | None = None
    weight: float | None = None
    duration_seconds: int | None = None
    distance_meters: int | None = None
    rpe: float | None = None
    rest_seconds: int | None = None
    comment: str | None = None


class PlannedRangeQuery(BaseModel):
    start: date
    end: date


class SessionFilter(BaseModel):
    start: datetime | None = None
    end: datetime | None = None

