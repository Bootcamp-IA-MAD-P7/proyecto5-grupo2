from fastapi.testclient import TestClient

from app.backend.main import app


client = TestClient(app)


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


def test_predict_returns_contract_shape() -> None:
    response = client.post("/predict", json=valid_prediction_payload())

    assert response.status_code == 200
    body = response.json()

    assert body["prediction"] in {"Canceled", "Not_Canceled"}
    assert body["prediction_label"] in {0, 1}
    assert 0 <= body["probability"] <= 1
    assert body["risk_level"] in {"low", "medium", "high"}
    assert body["risk_label"] in {"Bajo", "Medio", "Alto"}
    assert isinstance(body["model_version"], str)
    assert isinstance(body["main_factors"], list)
    assert isinstance(body["recommendation"], str)


def test_predict_model_version_matches_model_info() -> None:
    model_info = client.get("/model/info").json()
    prediction = client.post("/predict", json=valid_prediction_payload()).json()

    assert prediction["model_version"] == model_info["model_version"]


def test_predict_rejects_invalid_payload() -> None:
    payload = valid_prediction_payload()
    payload["lead_time"] = -1

    response = client.post("/predict", json=payload)

    assert response.status_code == 422
