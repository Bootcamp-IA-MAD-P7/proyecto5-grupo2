from uuid import uuid4

from sqlalchemy.orm import sessionmaker

from src.data.database import Base, create_database_engine
from src.data.feedback_ingestion import build_retraining_dataset, load_feedback_records
from src.data.models import PredictionFeedback
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


def create_feedback_database(tmp_path, *, actual_status: str | None) -> str:
    database_url = f"sqlite:///{(tmp_path / f'{uuid4()}.db').as_posix()}"
    database_engine = create_database_engine(database_url)
    Base.metadata.create_all(bind=database_engine)
    session_factory = sessionmaker(bind=database_engine, expire_on_commit=False)

    with session_factory() as session:
        session.add(
            PredictionFeedback(
                record_id=str(uuid4()),
                model_version="random_forest_champion_v0.1.0",
                prediction="Canceled",
                probability=0.83,
                risk_level="high",
                user_feedback="correct",
                actual_status=actual_status,
                source="unit_test",
                comments=None,
                input_data=sample_input(),
            )
        )
        session.commit()

    database_engine.dispose()
    return database_url


def test_load_feedback_records_returns_empty_dataframe_without_schema(tmp_path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'empty.db').as_posix()}"

    feedback = load_feedback_records(database_url)

    assert feedback.empty


def test_build_retraining_dataset_ignores_unlabeled_feedback(tmp_path) -> None:
    database_url = create_feedback_database(tmp_path, actual_status=None)

    retraining_data = build_retraining_dataset(database_url)

    assert retraining_data.empty
    assert list(retraining_data.columns) == FEATURE_COLUMNS + [TARGET_COLUMN]


def test_build_retraining_dataset_flattens_labeled_feedback(tmp_path) -> None:
    database_url = create_feedback_database(tmp_path, actual_status="Canceled")

    retraining_data = build_retraining_dataset(database_url)

    assert len(retraining_data) == 1
    assert list(retraining_data.columns) == FEATURE_COLUMNS + [TARGET_COLUMN]
    assert retraining_data.loc[0, "lead_time"] == 120
    assert retraining_data.loc[0, TARGET_COLUMN] == "Canceled"
