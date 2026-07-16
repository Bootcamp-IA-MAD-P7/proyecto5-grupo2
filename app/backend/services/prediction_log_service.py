"""Persistence service for the immutable prediction audit trail."""

from sqlalchemy import func, select

from app.backend.schemas import PredictionRequest, PredictionResponse
from src.data.database import SessionLocal
from src.data.models import PredictionLog


def save_prediction_log(
    payload: PredictionRequest,
    prediction: PredictionResponse,
    *,
    source: str = "api",
) -> None:
    """Persist a prediction before its successful API response is returned."""

    record = PredictionLog(
        prediction_id=prediction.prediction_id,
        model_version=prediction.model_version,
        prediction=prediction.prediction,
        prediction_label=prediction.prediction_label,
        probability=prediction.probability,
        risk_level=prediction.risk_level,
        source=source,
        input_data=payload.model_dump(),
    )

    with SessionLocal() as session:
        session.add(record)
        session.commit()


def count_prediction_logs() -> int:
    """Return the number of persisted predictions."""

    with SessionLocal() as session:
        return session.scalar(select(func.count()).select_from(PredictionLog)) or 0
