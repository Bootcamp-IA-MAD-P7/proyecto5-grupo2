"""Operational dependencies used by the API readiness endpoint."""

from datetime import UTC, datetime

from sqlalchemy import select

from app.backend.schemas import ReadinessResponse
from app.backend.services.model_service import load_model, load_model_metadata
from src.data.database import DATABASE_URL, SessionLocal, database_backend_name
from src.data.models import PredictionFeedback, PredictionLog


def get_readiness() -> ReadinessResponse:
    """Check that both the Champion and operational database are usable."""

    model_loaded = False
    model_version = "unavailable"
    try:
        load_model()
        model_version = load_model_metadata()["model_version"]
        model_loaded = True
    except Exception:
        model_loaded = False

    database_connected = False
    try:
        with SessionLocal() as session:
            session.execute(select(PredictionLog).limit(1))
            session.execute(select(PredictionFeedback).limit(1))
        database_connected = True
    except Exception:
        database_connected = False

    ready = model_loaded and database_connected
    return ReadinessResponse(
        status="ready" if ready else "not_ready",
        service="hotel-insights-api",
        version="0.1.0",
        checked_at=datetime.now(UTC),
        model_loaded=model_loaded,
        model_version=model_version,
        database_connected=database_connected,
        storage=database_backend_name(DATABASE_URL),
    )
