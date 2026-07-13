import csv
import json

from src.data.feedback_ingestion import build_retraining_dataset, load_feedback_records
from src.features.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN


def sample_input() -> dict:
    return {
        "no_of_adults": 2,
        "no_of_children": 0,
        "no_of_weekend_nights": 1,
        "no_of_week_nights": 2,
        "lead_time": 120,
        "arrival_year": 2018,
        "arrival_month": 7,
        "arrival_date": 15,
        "no_of_previous_cancellations": 0,
        "no_of_previous_bookings_not_canceled": 0,
        "avg_price_per_room": 156.0,
        "no_of_special_requests": 0,
        "type_of_meal_plan": "Meal Plan 1",
        "room_type_reserved": "Room_Type 1",
        "market_segment_type": "Online",
        "required_car_parking_space": 0,
        "repeated_guest": 0,
    }


def write_feedback_file(path, *, actual_status: str = "Canceled") -> None:
    fieldnames = [
        "record_id",
        "created_at",
        "model_version",
        "prediction",
        "probability",
        "risk_level",
        "user_feedback",
        "actual_status",
        "source",
        "comments",
        "input_json",
    ]
    row = {
        "record_id": "feedback-1",
        "created_at": "2026-07-13T10:00:00+00:00",
        "model_version": "random_forest_champion_v0.1.0",
        "prediction": "Canceled",
        "probability": 0.83,
        "risk_level": "high",
        "user_feedback": "correct",
        "actual_status": actual_status,
        "source": "unit_test",
        "comments": "",
        "input_json": json.dumps(sample_input(), sort_keys=True),
    }

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)


def test_load_feedback_records_returns_empty_dataframe_for_missing_file(tmp_path) -> None:
    feedback = load_feedback_records(tmp_path / "missing.csv")

    assert feedback.empty


def test_build_retraining_dataset_ignores_unlabeled_feedback(tmp_path) -> None:
    feedback_file = tmp_path / "prediction_feedback.csv"
    write_feedback_file(feedback_file, actual_status="")

    retraining_data = build_retraining_dataset(feedback_file)

    assert retraining_data.empty
    assert list(retraining_data.columns) == FEATURE_COLUMNS + [TARGET_COLUMN]


def test_build_retraining_dataset_flattens_labeled_feedback(tmp_path) -> None:
    feedback_file = tmp_path / "prediction_feedback.csv"
    write_feedback_file(feedback_file, actual_status="Canceled")

    retraining_data = build_retraining_dataset(feedback_file)

    assert len(retraining_data) == 1
    assert list(retraining_data.columns) == FEATURE_COLUMNS + [TARGET_COLUMN]
    assert retraining_data.loc[0, "lead_time"] == 120
    assert retraining_data.loc[0, TARGET_COLUMN] == "Canceled"
