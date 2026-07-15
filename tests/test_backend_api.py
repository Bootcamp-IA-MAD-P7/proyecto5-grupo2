from fastapi.testclient import TestClient
from sqlalchemy import select

from app.backend import main as backend_main
from app.backend.main import LOCAL_CORS_ORIGINS, app, get_cors_origins
from app.backend.services import feedback_service, health_service
from src.data.models import PredictionLog


client = TestClient(app)


def test_cors_origins_include_configured_deployment_domain(monkeypatch) -> None:
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://develop.example.amplifyapp.com/, https://hotel.example.com",
    )

    origins = get_cors_origins()

    assert origins[: len(LOCAL_CORS_ORIGINS)] == LOCAL_CORS_ORIGINS
    assert "https://develop.example.amplifyapp.com" in origins
    assert "https://hotel.example.com" in origins


def valid_prediction_payload() -> dict:
    return {
        "lead_time": 120,
        "arrival_year": 2018,
        "arrival_month": 7,
        "arrival_date": 15,
        "no_of_special_requests": 0,
        "avg_price_per_room": 156.0,
        "market_segment_type": "Online",
        "no_of_weekend_nights": 1,
        "no_of_week_nights": 2,
        "type_of_meal_plan": "Meal Plan 1",
        "room_type_reserved": "Room_Type 1",
        "no_of_adults": 2,
        "no_of_children": 0,
        "required_car_parking_space": 0,
        "repeated_guest": 0,
        "no_of_previous_cancellations": 0,
        "no_of_previous_bookings_not_canceled": 0,
    }


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "hotel-insights-api",
        "version": "0.1.0",
    }


def test_readiness_confirms_model_and_database() -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["model_loaded"] is True
    assert body["model_version"] == "random_forest_champion_v0.1.0"
    assert body["database_connected"] is True
    assert body["storage"] == "sqlite"


def test_readiness_returns_503_when_database_is_unavailable(monkeypatch) -> None:
    def unavailable_session():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(health_service, "SessionLocal", unavailable_session)

    response = client.get("/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["model_loaded"] is True
    assert body["database_connected"] is False


def test_request_id_is_returned_to_the_caller() -> None:
    response = client.get(
        "/health",
        headers={"X-Request-ID": "presentation-check-001"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "presentation-check-001"


def test_model_info_returns_loaded_champion_state() -> None:
    response = client.get("/model/info")

    assert response.status_code == 200
    body = response.json()

    assert body["model_loaded"] is True
    assert body["model_version"] == "random_forest_champion_v0.1.0"
    assert body["model_status"] == "loaded"
    assert body["model_type"] == "RandomForestClassifier"
    assert body["primary_metric"] == "f1_canceled"
    assert body["target"] == "booking_status"
    assert body["positive_class"] == "Canceled"
    assert isinstance(body["notes"], list)


def test_predict_returns_contract_shape(operational_database, monkeypatch) -> None:
    emitted_events = []
    monkeypatch.setattr(
        backend_main,
        "emit_log_event",
        lambda event, **fields: emitted_events.append({"event": event, **fields}),
    )
    response = client.post(
        "/predict",
        json=valid_prediction_payload(),
        headers={
            "X-Prediction-Source": "frontend_manual",
            "X-Request-ID": "prediction-check-001",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert isinstance(body["prediction_id"], str)
    assert len(body["prediction_id"]) == 36
    assert body["prediction"] in {"Canceled", "Not_Canceled"}
    assert body["prediction_label"] in {0, 1}
    assert 0 <= body["probability"] <= 1
    assert body["risk_level"] in {"low", "medium", "high"}
    assert body["risk_label"] in {"Bajo", "Medio", "Alto"}
    assert isinstance(body["model_version"], str)
    assert isinstance(body["main_factors"], list)
    assert isinstance(body["recommendation"], str)

    _, session_factory = operational_database
    with session_factory() as session:
        stored_prediction = session.scalar(
            select(PredictionLog).where(
                PredictionLog.prediction_id == body["prediction_id"]
            )
        )

    assert stored_prediction is not None
    assert stored_prediction.model_version == body["model_version"]
    assert stored_prediction.prediction == body["prediction"]
    assert stored_prediction.prediction_label == body["prediction_label"]
    assert stored_prediction.probability == body["probability"]
    assert stored_prediction.risk_level == body["risk_level"]
    assert stored_prediction.source == "frontend_manual"
    assert stored_prediction.input_data == valid_prediction_payload()

    prediction_event = next(
        event for event in emitted_events if event["event"] == "prediction_completed"
    )
    assert prediction_event["request_id"] == "prediction-check-001"
    assert prediction_event["prediction_id"] == body["prediction_id"]
    assert "input_data" not in prediction_event


def test_predict_rejects_unknown_prediction_source() -> None:
    response = client.post(
        "/predict",
        json=valid_prediction_payload(),
        headers={"X-Prediction-Source": "untrusted_source"},
    )

    assert response.status_code == 422


def test_predict_model_version_matches_model_info() -> None:
    model_info = client.get("/model/info").json()
    prediction = client.post("/predict", json=valid_prediction_payload()).json()

    assert prediction["model_version"] == model_info["model_version"]


def test_demo_reservations_return_real_dataset_payloads() -> None:
    response = client.get("/reservations/demo?limit=3")

    assert response.status_code == 200
    body = response.json()

    assert body["total_available"] > 0
    assert body["returned"] == 3
    assert body["source"].endswith("Hotel Reservations.csv")
    assert len(body["reservations"]) == 3

    reservation = body["reservations"][0]
    assert reservation["id"].startswith("INN")
    assert reservation["display_name"].startswith("Reserva INN")
    assert reservation["input_data"]["lead_time"] >= 0


def test_predict_rejects_invalid_payload() -> None:
    payload = valid_prediction_payload()
    payload["lead_time"] = -1

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def valid_feedback_payload() -> dict:
    prediction = client.post("/predict", json=valid_prediction_payload()).json()

    return {
        "input_data": valid_prediction_payload(),
        "prediction": prediction["prediction"],
        "probability": prediction["probability"],
        "risk_level": prediction["risk_level"],
        "model_version": prediction["model_version"],
        "user_feedback": "correct",
        "actual_status": prediction["prediction"],
        "comments": "Smoke feedback from API test.",
        "source": "api_test",
    }


def test_feedback_is_stored_and_counted(feedback_database) -> None:
    response = client.post("/feedback", json=valid_feedback_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "stored"
    assert body["stored"] is True
    assert isinstance(body["record_id"], str)

    summary = client.get("/feedback/summary")

    assert summary.status_code == 200
    assert summary.json()["total_records"] == 1
    assert summary.json()["storage"] == "sqlite"


def test_feedback_rejects_invalid_payload() -> None:
    payload = valid_feedback_payload()
    payload["user_feedback"] = "maybe"

    response = client.post("/feedback", json=payload)

    assert response.status_code == 422


def test_data_drift_returns_monitoring_contract(monkeypatch) -> None:
    monkeypatch.setattr(
        backend_main,
        "get_data_drift_report",
        lambda: {
            "profile_version": "training_reference_v1",
            "generated_at": "2026-07-15T10:00:00+00:00",
            "data_source": "prediction_logs",
            "sample_limit": 1000,
            "excluded_sources": ["frontend_demo_queue", "prediction_api"],
            "reference_rows": 25391,
            "current_rows": 2,
            "minimum_current_rows": 100,
            "thresholds": {"moderate": 0.10, "high": 0.25},
            "status": "insufficient_data",
            "max_psi": None,
            "drifted_features": [],
            "features": [],
            "message": "At least 100 current records are required; only 2 are available.",
        },
    )

    response = client.get("/monitoring/drift")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "insufficient_data"
    assert body["profile_version"] == "training_reference_v1"
    assert body["data_source"] == "prediction_logs"
    assert body["excluded_sources"] == ["frontend_demo_queue", "prediction_api"]
    assert body["current_rows"] == 2
    assert body["minimum_current_rows"] == 100
    assert body["features"] == []
