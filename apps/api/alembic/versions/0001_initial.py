"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-18
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "exercises",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("modality", sa.String(length=40), nullable=False),
        sa.Column("default_measure_type", sa.String(length=40), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercises")),
        sa.UniqueConstraint("name", name=op.f("uq_exercises_name")),
    )
    op.create_index(op.f("ix_exercises_name"), "exercises", ["name"], unique=True)

    op.create_table(
        "workout_templates",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_workout_templates_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workout_templates")),
    )
    op.create_index(op.f("ix_workout_templates_user_id"), "workout_templates", ["user_id"], unique=False)

    op.create_table(
        "training_blocks",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("goal", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_training_blocks_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_training_blocks")),
    )
    op.create_index(op.f("ix_training_blocks_user_id"), "training_blocks", ["user_id"], unique=False)

    op.create_table(
        "workout_template_exercises",
        sa.Column("template_id", sa.String(), nullable=False),
        sa.Column("exercise_id", sa.String(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("target_sets", sa.Integer(), nullable=True),
        sa.Column("target_reps", sa.String(length=50), nullable=True),
        sa.Column("target_weight", sa.Float(), nullable=True),
        sa.Column("target_duration_seconds", sa.Integer(), nullable=True),
        sa.Column("target_distance_meters", sa.Integer(), nullable=True),
        sa.Column("target_rpe", sa.Float(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["exercise_id"], ["exercises.id"], name=op.f("fk_workout_template_exercises_exercise_id_exercises")
        ),
        sa.ForeignKeyConstraint(
            ["template_id"], ["workout_templates.id"], name=op.f("fk_workout_template_exercises_template_id_workout_templates"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workout_template_exercises")),
    )
    op.create_index(op.f("ix_workout_template_exercises_exercise_id"), "workout_template_exercises", ["exercise_id"], unique=False)
    op.create_index(op.f("ix_workout_template_exercises_template_id"), "workout_template_exercises", ["template_id"], unique=False)

    op.create_table(
        "progression_rules",
        sa.Column("training_block_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("rule_type", sa.String(length=50), nullable=False),
        sa.Column("config_json", sa.JSON(), nullable=True),
        sa.Column("deload_strategy", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["training_block_id"], ["training_blocks.id"], name=op.f("fk_progression_rules_training_block_id_training_blocks"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_progression_rules")),
    )
    op.create_index(op.f("ix_progression_rules_training_block_id"), "progression_rules", ["training_block_id"], unique=False)

    op.create_table(
        "block_workouts",
        sa.Column("training_block_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("week_index", sa.Integer(), nullable=False),
        sa.Column("day_index", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["training_block_id"], ["training_blocks.id"], name=op.f("fk_block_workouts_training_block_id_training_blocks"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_block_workouts")),
    )
    op.create_index(op.f("ix_block_workouts_training_block_id"), "block_workouts", ["training_block_id"], unique=False)

    op.create_table(
        "planned_workouts",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("planned_date", sa.Date(), nullable=False),
        sa.Column("planned_start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("training_block_id", sa.String(), nullable=True),
        sa.Column("block_workout_id", sa.String(), nullable=True),
        sa.Column("workout_template_id", sa.String(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["block_workout_id"], ["block_workouts.id"], name=op.f("fk_planned_workouts_block_workout_id_block_workouts")),
        sa.ForeignKeyConstraint(["training_block_id"], ["training_blocks.id"], name=op.f("fk_planned_workouts_training_block_id_training_blocks")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_planned_workouts_user_id_users")),
        sa.ForeignKeyConstraint(["workout_template_id"], ["workout_templates.id"], name=op.f("fk_planned_workouts_workout_template_id_workout_templates")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_planned_workouts")),
    )
    op.create_index(op.f("ix_planned_workouts_planned_date"), "planned_workouts", ["planned_date"], unique=False)
    op.create_index(op.f("ix_planned_workouts_user_id"), "planned_workouts", ["user_id"], unique=False)

    op.create_table(
        "block_workout_exercises",
        sa.Column("block_workout_id", sa.String(), nullable=False),
        sa.Column("exercise_id", sa.String(), nullable=False),
        sa.Column("progression_rule_id", sa.String(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("target_sets", sa.Integer(), nullable=True),
        sa.Column("target_reps", sa.String(length=50), nullable=True),
        sa.Column("target_weight", sa.Float(), nullable=True),
        sa.Column("target_duration_seconds", sa.Integer(), nullable=True),
        sa.Column("target_distance_meters", sa.Integer(), nullable=True),
        sa.Column("target_rpe", sa.Float(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["block_workout_id"], ["block_workouts.id"], name=op.f("fk_block_workout_exercises_block_workout_id_block_workouts"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], name=op.f("fk_block_workout_exercises_exercise_id_exercises")),
        sa.ForeignKeyConstraint(["progression_rule_id"], ["progression_rules.id"], name=op.f("fk_block_workout_exercises_progression_rule_id_progression_rules")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_block_workout_exercises")),
    )
    op.create_index(op.f("ix_block_workout_exercises_block_workout_id"), "block_workout_exercises", ["block_workout_id"], unique=False)
    op.create_index(op.f("ix_block_workout_exercises_exercise_id"), "block_workout_exercises", ["exercise_id"], unique=False)

    op.create_table(
        "planned_workout_exercises",
        sa.Column("planned_workout_id", sa.String(), nullable=False),
        sa.Column("exercise_id", sa.String(), nullable=False),
        sa.Column("progression_rule_id", sa.String(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("exercise_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("target_sets", sa.Integer(), nullable=True),
        sa.Column("target_reps", sa.String(length=50), nullable=True),
        sa.Column("target_weight", sa.Float(), nullable=True),
        sa.Column("target_duration_seconds", sa.Integer(), nullable=True),
        sa.Column("target_distance_meters", sa.Integer(), nullable=True),
        sa.Column("target_rpe", sa.Float(), nullable=True),
        sa.Column("progression_snapshot_json", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], name=op.f("fk_planned_workout_exercises_exercise_id_exercises")),
        sa.ForeignKeyConstraint(["planned_workout_id"], ["planned_workouts.id"], name=op.f("fk_planned_workout_exercises_planned_workout_id_planned_workouts"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["progression_rule_id"], ["progression_rules.id"], name=op.f("fk_planned_workout_exercises_progression_rule_id_progression_rules")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_planned_workout_exercises")),
    )
    op.create_index(op.f("ix_planned_workout_exercises_exercise_id"), "planned_workout_exercises", ["exercise_id"], unique=False)
    op.create_index(op.f("ix_planned_workout_exercises_planned_workout_id"), "planned_workout_exercises", ["planned_workout_id"], unique=False)

    op.create_table(
        "workout_sessions",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("planned_workout_id", sa.String(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("session_notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["planned_workout_id"], ["planned_workouts.id"], name=op.f("fk_workout_sessions_planned_workout_id_planned_workouts")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_workout_sessions_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workout_sessions")),
        sa.UniqueConstraint("planned_workout_id", name=op.f("uq_workout_sessions_planned_workout_id")),
    )
    op.create_index(op.f("ix_workout_sessions_user_id"), "workout_sessions", ["user_id"], unique=False)

    op.create_table(
        "workout_session_exercises",
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("exercise_id", sa.String(), nullable=True),
        sa.Column("planned_workout_exercise_id", sa.String(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("exercise_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("target_sets", sa.Integer(), nullable=True),
        sa.Column("target_reps", sa.String(length=50), nullable=True),
        sa.Column("target_weight", sa.Float(), nullable=True),
        sa.Column("target_duration_seconds", sa.Integer(), nullable=True),
        sa.Column("target_distance_meters", sa.Integer(), nullable=True),
        sa.Column("target_rpe", sa.Float(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], name=op.f("fk_workout_session_exercises_exercise_id_exercises")),
        sa.ForeignKeyConstraint(["planned_workout_exercise_id"], ["planned_workout_exercises.id"], name=op.f("fk_workout_session_exercises_planned_workout_exercise_id_planned_workout_exercises")),
        sa.ForeignKeyConstraint(["session_id"], ["workout_sessions.id"], name=op.f("fk_workout_session_exercises_session_id_workout_sessions"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workout_session_exercises")),
    )
    op.create_index(op.f("ix_workout_session_exercises_exercise_id"), "workout_session_exercises", ["exercise_id"], unique=False)
    op.create_index(op.f("ix_workout_session_exercises_session_id"), "workout_session_exercises", ["session_id"], unique=False)

    op.create_table(
        "set_entries",
        sa.Column("session_exercise_id", sa.String(), nullable=False),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("set_type", sa.String(length=40), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("distance_meters", sa.Integer(), nullable=True),
        sa.Column("rpe", sa.Float(), nullable=True),
        sa.Column("rest_seconds", sa.Integer(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_exercise_id"], ["workout_session_exercises.id"], name=op.f("fk_set_entries_session_exercise_id_workout_session_exercises"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_set_entries")),
    )
    op.create_index(op.f("ix_set_entries_session_exercise_id"), "set_entries", ["session_exercise_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_set_entries_session_exercise_id"), table_name="set_entries")
    op.drop_table("set_entries")
    op.drop_index(op.f("ix_workout_session_exercises_session_id"), table_name="workout_session_exercises")
    op.drop_index(op.f("ix_workout_session_exercises_exercise_id"), table_name="workout_session_exercises")
    op.drop_table("workout_session_exercises")
    op.drop_index(op.f("ix_workout_sessions_user_id"), table_name="workout_sessions")
    op.drop_table("workout_sessions")
    op.drop_index(op.f("ix_planned_workout_exercises_planned_workout_id"), table_name="planned_workout_exercises")
    op.drop_index(op.f("ix_planned_workout_exercises_exercise_id"), table_name="planned_workout_exercises")
    op.drop_table("planned_workout_exercises")
    op.drop_index(op.f("ix_block_workout_exercises_exercise_id"), table_name="block_workout_exercises")
    op.drop_index(op.f("ix_block_workout_exercises_block_workout_id"), table_name="block_workout_exercises")
    op.drop_table("block_workout_exercises")
    op.drop_index(op.f("ix_planned_workouts_user_id"), table_name="planned_workouts")
    op.drop_index(op.f("ix_planned_workouts_planned_date"), table_name="planned_workouts")
    op.drop_table("planned_workouts")
    op.drop_index(op.f("ix_block_workouts_training_block_id"), table_name="block_workouts")
    op.drop_table("block_workouts")
    op.drop_index(op.f("ix_progression_rules_training_block_id"), table_name="progression_rules")
    op.drop_table("progression_rules")
    op.drop_index(op.f("ix_workout_template_exercises_template_id"), table_name="workout_template_exercises")
    op.drop_index(op.f("ix_workout_template_exercises_exercise_id"), table_name="workout_template_exercises")
    op.drop_table("workout_template_exercises")
    op.drop_index(op.f("ix_training_blocks_user_id"), table_name="training_blocks")
    op.drop_table("training_blocks")
    op.drop_index(op.f("ix_workout_templates_user_id"), table_name="workout_templates")
    op.drop_table("workout_templates")
    op.drop_index(op.f("ix_exercises_name"), table_name="exercises")
    op.drop_table("exercises")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
