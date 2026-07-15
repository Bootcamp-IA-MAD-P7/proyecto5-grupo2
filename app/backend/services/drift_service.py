"""Application service for production input drift monitoring."""

from app.backend.schemas import DriftReportResponse
from src.data.feedback_ingestion import load_feedback_records
from src.mlops.data_drift import (
    calculate_drift_report,
    feedback_records_to_features,
    load_reference_profile,
)


def get_data_drift_report() -> DriftReportResponse:
    """Compare stored production inputs with the frozen training profile."""

    feedback_records = load_feedback_records()
    current_features = feedback_records_to_features(feedback_records)
    report = calculate_drift_report(load_reference_profile(), current_features)
    return DriftReportResponse.model_validate(report)
