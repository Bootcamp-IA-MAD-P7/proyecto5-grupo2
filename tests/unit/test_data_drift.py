import json

import pandas as pd

from app.backend.services import drift_service
from src.features.preprocessing import FEATURE_COLUMNS, load_dataset, prepare_data_splits
from src.mlops.data_drift import (
    build_reference_profile,
    calculate_drift_report,
    prediction_records_to_features,
)


def training_features() -> pd.DataFrame:
    return prepare_data_splits(load_dataset()).X_train


def test_drift_report_requires_enough_current_records() -> None:
    reference = training_features()
    profile = build_reference_profile(reference)

    report = calculate_drift_report(profile, reference.head(20))

    assert report["status"] == "insufficient_data"
    assert report["current_rows"] == 20
    assert report["features"] == []


def test_same_distribution_is_stable() -> None:
    reference = training_features()
    profile = build_reference_profile(reference)

    report = calculate_drift_report(profile, reference.copy())

    assert report["status"] == "stable"
    assert report["max_psi"] < 0.10
    assert report["drifted_features"] == []


def test_shifted_distribution_detects_high_drift() -> None:
    reference = training_features()
    profile = build_reference_profile(reference)
    shifted = reference.head(300).copy()
    shifted["lead_time"] = shifted["lead_time"] + 1000
    shifted["market_segment_type"] = "New_Channel"

    report = calculate_drift_report(profile, shifted)

    assert report["status"] == "drift_detected"
    assert "lead_time" in report["drifted_features"]
    assert "market_segment_type" in report["drifted_features"]
    assert {result["feature"] for result in report["features"]} == set(FEATURE_COLUMNS)


def test_prediction_records_extract_only_complete_model_inputs() -> None:
    valid_payload = training_features().iloc[0].to_dict()
    incomplete_payload = valid_payload.copy()
    incomplete_payload.pop("lead_time")
    predictions = pd.DataFrame(
        {
            "input_data": [
                valid_payload,
                json.dumps(valid_payload),
                incomplete_payload,
                "not-json",
                None,
            ]
        }
    )

    features = prediction_records_to_features(predictions)

    assert len(features) == 2
    assert features.columns.tolist() == FEATURE_COLUMNS
    assert features["lead_time"].tolist() == [
        valid_payload["lead_time"],
        valid_payload["lead_time"],
    ]


def test_operational_drift_service_uses_prediction_audit_rows(monkeypatch) -> None:
    prediction_records = pd.DataFrame(
        {"input_data": training_features().head(20).to_dict(orient="records")}
    )
    monkeypatch.setattr(
        drift_service,
        "load_prediction_records",
        lambda: prediction_records,
    )

    report = drift_service.get_data_drift_report()

    assert report.data_source == "prediction_logs"
    assert report.sample_limit == 1000
    assert report.excluded_sources == ["frontend_demo_queue", "prediction_api"]
    assert report.current_rows == 20
    assert report.status == "insufficient_data"
