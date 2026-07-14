"""Operational database models."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from src.data.database import Base


class PredictionFeedback(Base):
    """Prediction context and its optional observed outcome."""

    __tablename__ = "prediction_feedback"

    record_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    model_version: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    prediction: Mapped[str] = mapped_column(String(20), nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    user_feedback: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    actual_status: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(80), nullable=False)
    comments: Mapped[str | None] = mapped_column(String(500), nullable=True)
    input_data: Mapped[dict] = mapped_column(JSON, nullable=False)
