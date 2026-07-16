import logging
import os
from time import perf_counter
from typing import Annotated, Literal

from fastapi import FastAPI, Header, HTTPException, Path, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .observability import emit_log_event, resolve_request_id

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
    MonitoringExperimentsResponse,
    PredictionRequest,
    PredictionResponse,
    ReadinessResponse,
)
from .services.drift_service import get_data_drift_report
from .services.feedback_service import (
    get_feedback_history,
    get_feedback_summary,
    save_feedback,
    update_feedback_record,
)
from .services.experiment_service import get_experiment_overview
from .services.health_service import get_readiness
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


@app.middleware("http")
async def observe_request(request: Request, call_next):
    request_id = resolve_request_id(request.headers.get("X-Request-ID"))
    request.state.request_id = request_id
    started_at = perf_counter()

    try:
        response = await call_next(request)
    except Exception as error:
        emit_log_event(
            "request_failed",
            level=logging.ERROR,
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            duration_ms=round((perf_counter() - started_at) * 1000, 2),
            error_type=type(error).__name__,
        )
        raise

    response.headers["X-Request-ID"] = request_id
    emit_log_event(
        "request_completed",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round((perf_counter() - started_at) * 1000, 2),
    )
    return response


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.get(
    "/health/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse}},
)
def readiness() -> ReadinessResponse | JSONResponse:
    readiness_state = get_readiness()
    if readiness_state.status != "ready":
        return JSONResponse(
            status_code=503,
            content=readiness_state.model_dump(mode="json"),
        )
    return readiness_state


@app.get("/model/info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    return get_model_info()


@app.post("/predict", response_model=PredictionResponse)
def predict(
    payload: PredictionRequest,
    request: Request,
    prediction_source: Annotated[
        Literal["api", "frontend_manual", "frontend_demo_queue"],
        Header(alias="X-Prediction-Source"),
    ] = "api",
) -> PredictionResponse:
    prediction = predict_cancellation(payload)
    save_prediction_log(payload, prediction, source=prediction_source)
    emit_log_event(
        "prediction_completed",
        request_id=request.state.request_id,
        prediction_id=prediction.prediction_id,
        model_version=prediction.model_version,
        prediction_source=prediction_source,
        risk_level=prediction.risk_level,
    )
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


@app.get("/monitoring/experiments", response_model=MonitoringExperimentsResponse)
def monitoring_experiments() -> MonitoringExperimentsResponse:
    return get_experiment_overview()
