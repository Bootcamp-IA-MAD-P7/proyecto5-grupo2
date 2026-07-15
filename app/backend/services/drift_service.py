"""Application service for production input drift monitoring."""

from app.backend.schemas import DriftReportResponse
from src.data.prediction_ingestion import (
    DRIFT_EXCLUDED_SOURCES,
    DRIFT_SAMPLE_LIMIT,
    load_prediction_records,
)
from src.mlops.data_drift import (
    calculate_drift_report,
    load_reference_profile,
    prediction_records_to_features,
)


def get_data_drift_report() -> DriftReportResponse:
    """Compare stored production inputs with the frozen training profile."""

    prediction_records = load_prediction_records()
    current_features = prediction_records_to_features(prediction_records)
    report = calculate_drift_report(load_reference_profile(), current_features)
    report.update(
        {
            "data_source": "prediction_logs",
            "sample_limit": DRIFT_SAMPLE_LIMIT,
            "excluded_sources": list(DRIFT_EXCLUDED_SOURCES),
        }
    )
    return DriftReportResponse.model_validate(report)
