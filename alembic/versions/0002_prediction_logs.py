"""Create the prediction audit log.

Revision ID: 0002_prediction_logs
Revises: 0001_prediction_feedback
Create Date: 2026-07-15
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_prediction_logs"
down_revision: str | None = "0001_prediction_feedback"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "prediction_logs"
INDEXES = {
    "ix_prediction_logs_created_at": ["created_at"],
    "ix_prediction_logs_model_version": ["model_version"],
}


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("prediction_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_version", sa.String(length=120), nullable=False),
        sa.Column("prediction", sa.String(length=20), nullable=False),
        sa.Column("prediction_label", sa.Integer(), nullable=False),
        sa.Column("probability", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("input_data", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("prediction_id"),
    )
    for index_name, columns in INDEXES.items():
        op.create_index(index_name, TABLE_NAME, columns, unique=False)


def downgrade() -> None:
    for index_name in INDEXES:
        op.drop_index(index_name, table_name=TABLE_NAME)
    op.drop_table(TABLE_NAME)
