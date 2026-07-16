import os
from typing import Annotated, Literal

from fastapi import FastAPI, Header, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    DriftReportResponse,
    FeedbackRequest,
    FeedbackHistoryResponse,
    FeedbackRecordResponse,
    FeedbackResponse,
    FeedbackSummaryResponse,
    FeedbackUpdateRequest,
    DemoReservationResponse,
    DemoReservationsResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictionRequest,
    PredictionResponse,
)
from .services.drift_service import get_data_drift_report
from .services.feedback_service import (
    get_feedback_history,
    get_feedback_summary,
    save_feedback,
    update_feedback_record,
)
from .services.model_service import get_model_info, predict_cancellation
from .services.prediction_log_service import save_prediction_log
from .services.reservation_service import get_demo_reservation_by_id, get_demo_reservations


LOCAL_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]


def get_cors_origins() -> list[str]:
    """Combine local origins with deployment origins from the environment."""

    deployment_origins = [
        origin.strip().rstrip("/")
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    return list(dict.fromkeys([*LOCAL_CORS_ORIGINS, *deployment_origins]))


app = FastAPI(
    title="Hotel Insights API",
    version="0.1.0",
    description="Initial prediction API for hotel reservation cancellation risk.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/model/info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    return get_model_info()


@app.post("/predict", response_model=PredictionResponse)
def predict(
    payload: PredictionRequest,
    prediction_source: Annotated[
        Literal["api", "frontend_manual", "frontend_demo_queue"],
        Header(alias="X-Prediction-Source"),
    ] = "api",
) -> PredictionResponse:
    prediction = predict_cancellation(payload)
    save_prediction_log(payload, prediction, source=prediction_source)
    return prediction


@app.get("/reservations/demo", response_model=DemoReservationsResponse)
def demo_reservations(
    limit: Annotated[int, Query(ge=1, le=50)] = 8,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> DemoReservationsResponse:
    return get_demo_reservations(limit=limit, offset=offset)


@app.get("/reservations/demo/{booking_id}", response_model=DemoReservationResponse)
def demo_reservation_by_id(
    booking_id: Annotated[str, Path(pattern=r"^INN\d{5}$")],
) -> DemoReservationResponse:
    reservation = get_demo_reservation_by_id(booking_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found.")
    return reservation


@app.post("/feedback", response_model=FeedbackResponse)
def feedback(payload: FeedbackRequest) -> FeedbackResponse:
    return save_feedback(payload)


@app.get("/feedback/summary", response_model=FeedbackSummaryResponse)
def feedback_summary() -> FeedbackSummaryResponse:
    return get_feedback_summary()


@app.get("/feedback", response_model=FeedbackHistoryResponse)
def feedback_history() -> FeedbackHistoryResponse:
    return get_feedback_history()


@app.patch("/feedback/{record_id}", response_model=FeedbackRecordResponse)
def update_feedback(
    record_id: str,
    payload: FeedbackUpdateRequest,
) -> FeedbackRecordResponse:
    updated_record = update_feedback_record(record_id, payload)
    if updated_record is None:
        raise HTTPException(status_code=404, detail="Feedback no encontrado.")
    return updated_record


@app.get("/monitoring/drift", response_model=DriftReportResponse)
def data_drift() -> DriftReportResponse:
    return get_data_drift_report()
