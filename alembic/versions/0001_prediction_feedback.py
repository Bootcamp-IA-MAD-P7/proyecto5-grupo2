"""Create the initial prediction feedback schema.

Revision ID: 0001_prediction_feedback
Revises:
Create Date: 2026-07-15
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_prediction_feedback"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE_NAME = "prediction_feedback"
EXPECTED_COLUMNS = {
    "record_id",
    "created_at",
    "model_version",
    "prediction",
    "probability",
    "risk_level",
    "user_feedback",
    "actual_status",
    "source",
    "comments",
    "input_data",
}
INDEXES = {
    "ix_prediction_feedback_actual_status": ["actual_status"],
    "ix_prediction_feedback_model_version": ["model_version"],
    "ix_prediction_feedback_user_feedback": ["user_feedback"],
}


def _adopt_legacy_table(inspector: sa.Inspector) -> bool:
    """Validate and adopt the table created before Alembic was introduced."""

    if TABLE_NAME not in inspector.get_table_names():
        return False

    existing_columns = {column["name"] for column in inspector.get_columns(TABLE_NAME)}
    if existing_columns != EXPECTED_COLUMNS:
        missing = sorted(EXPECTED_COLUMNS - existing_columns)
        unexpected = sorted(existing_columns - EXPECTED_COLUMNS)
        raise RuntimeError(
            "Existing prediction_feedback schema does not match the Alembic baseline. "
            f"Missing columns: {missing}; unexpected columns: {unexpected}."
        )

    existing_indexes = {index["name"] for index in inspector.get_indexes(TABLE_NAME)}
    for index_name, columns in INDEXES.items():
        if index_name not in existing_indexes:
            op.create_index(index_name, TABLE_NAME, columns, unique=False)

    return True


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if _adopt_legacy_table(inspector):
        return

    op.create_table(
        TABLE_NAME,
        sa.Column("record_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_version", sa.String(length=120), nullable=False),
        sa.Column("prediction", sa.String(length=20), nullable=False),
        sa.Column("probability", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("user_feedback", sa.String(length=20), nullable=False),
        sa.Column("actual_status", sa.String(length=20), nullable=True),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("comments", sa.String(length=500), nullable=True),
        sa.Column("input_data", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("record_id"),
    )
    for index_name, columns in INDEXES.items():
        op.create_index(index_name, TABLE_NAME, columns, unique=False)


def downgrade() -> None:
    for index_name in INDEXES:
        op.drop_index(index_name, table_name=TABLE_NAME)
    op.drop_table(TABLE_NAME)
