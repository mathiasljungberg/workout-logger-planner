from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Modality(StrEnum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    CONDITIONING = "conditioning"
    MOBILITY = "mobility"
    OTHER = "other"


class MeasureType(StrEnum):
    REPS_WEIGHT = "reps_weight"
    DURATION = "duration"
    DISTANCE = "distance"
    MIXED = "mixed"


class WorkoutStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class SessionStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class RuleType(StrEnum):
    FIXED_INCREMENT = "fixed_increment"
    DOUBLE_PROGRESSION = "double_progression"
    PERCENT_BASED = "percent_based"
    MANUAL = "manual"


class SetType(StrEnum):
    WORK = "work"
    WARMUP = "warmup"
    DROP = "drop"
    AMRAP = "amrap"
    TIMED = "timed"


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))


class Exercise(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "exercises"

    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    modality: Mapped[str] = mapped_column(String(40), default=Modality.STRENGTH.value)
    default_measure_type: Mapped[str] = mapped_column(String(40), default=MeasureType.REPS_WEIGHT.value)
    notes: Mapped[str | None] = mapped_column(Text())
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class WorkoutTemplate(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workout_templates"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text())

    exercises: Mapped[list["WorkoutTemplateExercise"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="WorkoutTemplateExercise.order_index",
    )


class WorkoutTemplateExercise(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workout_template_exercises"

    template_id: Mapped[str] = mapped_column(ForeignKey("workout_templates.id", ondelete="CASCADE"), index=True)
    exercise_id: Mapped[str] = mapped_column(ForeignKey("exercises.id"), index=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text())
    target_sets: Mapped[int | None] = mapped_column(Integer)
    target_reps: Mapped[str | None] = mapped_column(String(50))
    target_weight: Mapped[float | None] = mapped_column(Float)
    target_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    target_distance_meters: Mapped[int | None] = mapped_column(Integer)
    target_rpe: Mapped[float | None] = mapped_column(Float)

    template: Mapped["WorkoutTemplate"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship()


class TrainingBlock(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "training_blocks"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    goal: Mapped[str | None] = mapped_column(Text())
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(40), default="draft")

    progression_rules: Mapped[list["ProgressionRule"]] = relationship(
        back_populates="training_block",
        cascade="all, delete-orphan",
    )
    workouts: Mapped[list["BlockWorkout"]] = relationship(
        back_populates="training_block",
        cascade="all, delete-orphan",
        order_by="BlockWorkout.week_index, BlockWorkout.day_index",
    )


class ProgressionRule(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "progression_rules"

    training_block_id: Mapped[str] = mapped_column(ForeignKey("training_blocks.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    rule_type: Mapped[str] = mapped_column(String(50), default=RuleType.FIXED_INCREMENT.value)
    config_json: Mapped[dict | None] = mapped_column(JSON, default=dict)
    deload_strategy: Mapped[str | None] = mapped_column(Text())
    notes: Mapped[str | None] = mapped_column(Text())

    training_block: Mapped["TrainingBlock"] = relationship(back_populates="progression_rules")


class BlockWorkout(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "block_workouts"

    training_block_id: Mapped[str] = mapped_column(ForeignKey("training_blocks.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    week_index: Mapped[int] = mapped_column(Integer, default=1)
    day_index: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[str | None] = mapped_column(Text())

    training_block: Mapped["TrainingBlock"] = relationship(back_populates="workouts")
    exercises: Mapped[list["BlockWorkoutExercise"]] = relationship(
        back_populates="block_workout",
        cascade="all, delete-orphan",
        order_by="BlockWorkoutExercise.order_index",
    )


class BlockWorkoutExercise(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "block_workout_exercises"

    block_workout_id: Mapped[str] = mapped_column(ForeignKey("block_workouts.id", ondelete="CASCADE"), index=True)
    exercise_id: Mapped[str] = mapped_column(ForeignKey("exercises.id"), index=True)
    progression_rule_id: Mapped[str | None] = mapped_column(ForeignKey("progression_rules.id"))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text())
    target_sets: Mapped[int | None] = mapped_column(Integer)
    target_reps: Mapped[str | None] = mapped_column(String(50))
    target_weight: Mapped[float | None] = mapped_column(Float)
    target_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    target_distance_meters: Mapped[int | None] = mapped_column(Integer)
    target_rpe: Mapped[float | None] = mapped_column(Float)

    block_workout: Mapped["BlockWorkout"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship()
    progression_rule: Mapped["ProgressionRule"] = relationship()


class PlannedWorkout(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "planned_workouts"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    planned_date: Mapped[date] = mapped_column(Date, index=True)
    planned_start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), default=WorkoutStatus.PLANNED.value)
    title: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text())
    training_block_id: Mapped[str | None] = mapped_column(ForeignKey("training_blocks.id"))
    block_workout_id: Mapped[str | None] = mapped_column(ForeignKey("block_workouts.id"))
    workout_template_id: Mapped[str | None] = mapped_column(ForeignKey("workout_templates.id"))

    exercises: Mapped[list["PlannedWorkoutExercise"]] = relationship(
        back_populates="planned_workout",
        cascade="all, delete-orphan",
        order_by="PlannedWorkoutExercise.order_index",
    )
    session: Mapped["WorkoutSession"] = relationship(back_populates="planned_workout", uselist=False)


class PlannedWorkoutExercise(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "planned_workout_exercises"

    planned_workout_id: Mapped[str] = mapped_column(ForeignKey("planned_workouts.id", ondelete="CASCADE"), index=True)
    exercise_id: Mapped[str] = mapped_column(ForeignKey("exercises.id"), index=True)
    progression_rule_id: Mapped[str | None] = mapped_column(ForeignKey("progression_rules.id"))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    exercise_name_snapshot: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text())
    target_sets: Mapped[int | None] = mapped_column(Integer)
    target_reps: Mapped[str | None] = mapped_column(String(50))
    target_weight: Mapped[float | None] = mapped_column(Float)
    target_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    target_distance_meters: Mapped[int | None] = mapped_column(Integer)
    target_rpe: Mapped[float | None] = mapped_column(Float)
    progression_snapshot_json: Mapped[dict | None] = mapped_column(JSON, default=dict)

    planned_workout: Mapped["PlannedWorkout"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship()
    progression_rule: Mapped["ProgressionRule"] = relationship()


class WorkoutSession(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workout_sessions"

    __table_args__ = (UniqueConstraint("planned_workout_id"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    planned_workout_id: Mapped[str | None] = mapped_column(ForeignKey("planned_workouts.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), default=SessionStatus.IN_PROGRESS.value)
    title: Mapped[str] = mapped_column(String(200))
    session_notes: Mapped[str | None] = mapped_column(Text())

    exercises: Mapped[list["WorkoutSessionExercise"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="WorkoutSessionExercise.order_index",
    )
    planned_workout: Mapped["PlannedWorkout | None"] = relationship(back_populates="session")


class WorkoutSessionExercise(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workout_session_exercises"

    session_id: Mapped[str] = mapped_column(ForeignKey("workout_sessions.id", ondelete="CASCADE"), index=True)
    exercise_id: Mapped[str | None] = mapped_column(ForeignKey("exercises.id"), index=True)
    planned_workout_exercise_id: Mapped[str | None] = mapped_column(ForeignKey("planned_workout_exercises.id"))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    exercise_name_snapshot: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text())
    target_sets: Mapped[int | None] = mapped_column(Integer)
    target_reps: Mapped[str | None] = mapped_column(String(50))
    target_weight: Mapped[float | None] = mapped_column(Float)
    target_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    target_distance_meters: Mapped[int | None] = mapped_column(Integer)
    target_rpe: Mapped[float | None] = mapped_column(Float)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    session: Mapped["WorkoutSession"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise | None"] = relationship()
    set_entries: Mapped[list["SetEntry"]] = relationship(
        back_populates="session_exercise",
        cascade="all, delete-orphan",
        order_by="SetEntry.set_number",
    )


class SetEntry(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "set_entries"

    session_exercise_id: Mapped[str] = mapped_column(
        ForeignKey("workout_session_exercises.id", ondelete="CASCADE"),
        index=True,
    )
    set_number: Mapped[int] = mapped_column(Integer)
    set_type: Mapped[str] = mapped_column(String(40), default=SetType.WORK.value)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    reps: Mapped[int | None] = mapped_column(Integer)
    weight: Mapped[float | None] = mapped_column(Float)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    distance_meters: Mapped[int | None] = mapped_column(Integer)
    rpe: Mapped[float | None] = mapped_column(Float)
    rest_seconds: Mapped[int | None] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text())

    session_exercise: Mapped["WorkoutSessionExercise"] = relationship(back_populates="set_entries")

