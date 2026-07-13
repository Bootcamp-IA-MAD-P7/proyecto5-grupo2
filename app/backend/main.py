from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    FeedbackRequest,
    FeedbackResponse,
    FeedbackSummaryResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictionRequest,
    PredictionResponse,
)
from .services.feedback_service import get_feedback_summary, save_feedback
from .services.model_service import get_model_info, predict_cancellation


app = FastAPI(
    title="Hotel Insights API",
    version="0.1.0",
    description="Initial prediction API for hotel reservation cancellation risk.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
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
def predict(payload: PredictionRequest) -> PredictionResponse:
    return predict_cancellation(payload)


@app.post("/feedback", response_model=FeedbackResponse)
def feedback(payload: FeedbackRequest) -> FeedbackResponse:
    return save_feedback(payload)


@app.get("/feedback/summary", response_model=FeedbackSummaryResponse)
def feedback_summary() -> FeedbackSummaryResponse:
    return get_feedback_summary()
