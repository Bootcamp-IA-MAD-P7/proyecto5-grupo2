from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from src.data.database import Base, create_database_engine
from src.data.models import PredictionLog
from src.data.prediction_ingestion import load_prediction_records


def sample_input(lead_time: int) -> dict:
    return {
        "no_of_adults": 2,
        "no_of_children": 0,
        "no_of_weekend_nights": 1,
        "no_of_week_nights": 2,
        "lead_time": lead_time,
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


def add_prediction(
    session: Session,
    *,
    source: str,
    lead_time: int,
    created_at: datetime,
) -> None:
    session.add(
        PredictionLog(
            prediction_id=str(uuid4()),
            created_at=created_at,
            model_version="random_forest_champion_v0.1.0",
            prediction="Canceled",
            prediction_label=1,
            probability=0.83,
            risk_level="high",
            source=source,
            input_data=sample_input(lead_time),
        )
    )


def test_load_prediction_records_excludes_demo_and_limits_recent_rows(tmp_path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'predictions.db').as_posix()}"
    database_engine = create_database_engine(database_url)
    Base.metadata.create_all(bind=database_engine)
    now = datetime.now(UTC)

    with Session(database_engine) as session:
        add_prediction(
            session,
            source="frontend_manual",
            lead_time=10,
            created_at=now - timedelta(minutes=2),
        )
        add_prediction(
            session,
            source="api",
            lead_time=20,
            created_at=now - timedelta(minutes=1),
        )
        add_prediction(
            session,
            source="frontend_demo_queue",
            lead_time=999,
            created_at=now,
        )
        add_prediction(
            session,
            source="prediction_api",
            lead_time=888,
            created_at=now + timedelta(minutes=1),
        )
        session.commit()

    records = load_prediction_records(database_url, limit=1)

    assert len(records) == 1
    assert records.iloc[0]["source"] == "api"
    assert records.iloc[0]["input_data"]["lead_time"] == 20
    database_engine.dispose()


def test_load_prediction_records_returns_empty_without_schema(tmp_path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'empty.db').as_posix()}"

    records = load_prediction_records(database_url)

    assert records.empty


def test_load_prediction_records_rejects_invalid_limit() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        load_prediction_records(limit=0)
