"""add manual_override and progression_snapshot_json to block_workout_exercises

Revision ID: 0002_manual_override
Revises: 0001_initial
Create Date: 2026-04-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_manual_override"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "block_workout_exercises",
        sa.Column("manual_override", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "block_workout_exercises",
        sa.Column("progression_snapshot_json", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("block_workout_exercises", "progression_snapshot_json")
    op.drop_column("block_workout_exercises", "manual_override")
