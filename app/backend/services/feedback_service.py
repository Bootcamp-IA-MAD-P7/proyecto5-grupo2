from uuid import uuid4

from sqlalchemy import func, select

from app.backend.schemas import FeedbackRequest, FeedbackResponse, FeedbackSummaryResponse
from src.data.database import DATABASE_URL, SessionLocal, database_backend_name
from src.data.models import PredictionFeedback


def save_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    record_id = str(uuid4())

    record = PredictionFeedback(
        record_id=record_id,
        model_version=payload.model_version,
        prediction=payload.prediction,
        probability=payload.probability,
        risk_level=payload.risk_level,
        user_feedback=payload.user_feedback,
        actual_status=payload.actual_status,
        source=payload.source,
        comments=payload.comments,
        input_data=payload.input_data.model_dump(),
    )

    with SessionLocal() as session:
        session.add(record)
        session.commit()

    return FeedbackResponse(status="stored", record_id=record_id, stored=True)


def get_feedback_summary() -> FeedbackSummaryResponse:
    with SessionLocal() as session:
        total_records = session.scalar(select(func.count()).select_from(PredictionFeedback)) or 0

    return FeedbackSummaryResponse(
        total_records=total_records,
        storage=database_backend_name(DATABASE_URL),
    )
