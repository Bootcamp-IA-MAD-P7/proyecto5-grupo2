from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "hotel-insights-api"
    version: str = "0.1.0"


class ModelInfoResponse(BaseModel):
    model_loaded: bool
    model_version: str
    model_status: str
    model_type: str
    primary_metric: str
    target: str
    positive_class: str
    notes: list[str]


class PredictionRequest(BaseModel):
    lead_time: int = Field(..., ge=0)
    arrival_year: int = Field(..., ge=2000)
    arrival_month: int = Field(..., ge=1, le=12)
    arrival_date: int = Field(..., ge=1, le=31)
    no_of_special_requests: int = Field(..., ge=0)
    avg_price_per_room: float = Field(..., ge=0)
    market_segment_type: str
    no_of_weekend_nights: int = Field(..., ge=0)
    no_of_week_nights: int = Field(..., ge=0)
    type_of_meal_plan: str
    room_type_reserved: str
    no_of_adults: int = Field(..., ge=0)
    no_of_children: int = Field(..., ge=0)
    required_car_parking_space: int = Field(..., ge=0, le=1)
    repeated_guest: int = Field(..., ge=0, le=1)
    no_of_previous_cancellations: int = Field(..., ge=0)
    no_of_previous_bookings_not_canceled: int = Field(..., ge=0)


class PredictionResponse(BaseModel):
    prediction: str
    prediction_label: int
    probability: float = Field(..., ge=0, le=1)
    risk_level: str
    risk_label: str
    model_version: str
    main_factors: list[str]
    recommendation: str


class FeedbackRequest(BaseModel):
    input_data: PredictionRequest
    prediction: Literal["Canceled", "Not_Canceled"]
    probability: float = Field(..., ge=0, le=1)
    risk_level: Literal["low", "medium", "high"]
    model_version: str
    user_feedback: Literal["correct", "incorrect", "unknown"]
    actual_status: Literal["Canceled", "Not_Canceled"] | None = None
    comments: str | None = Field(default=None, max_length=500)
    source: str = Field(default="web_app", max_length=80)


class FeedbackResponse(BaseModel):
    status: str
    record_id: str
    stored: bool


class FeedbackSummaryResponse(BaseModel):
    total_records: int
    storage: str
