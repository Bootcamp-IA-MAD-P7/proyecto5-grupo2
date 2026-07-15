from fastapi.testclient import TestClient

from app.backend.main import app


client = TestClient(app)


def feedback_payload() -> dict:
    return {
        "input_data": {
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
        },
        "prediction": "Canceled",
        "probability": 0.83,
        "risk_level": "high",
        "model_version": "random_forest_champion_v0.1.0",
        "user_feedback": "correct",
        "actual_status": "Canceled",
        "comments": "Feedback para la prueba de histórico.",
        "source": "integration_test",
    }


def test_feedback_history_returns_empty_collection(feedback_database) -> None:
    response = client.get("/feedback")

    assert response.status_code == 200
    assert response.json() == {"total_records": 0, "records": []}


def test_feedback_history_can_be_listed_and_edited(feedback_database) -> None:
    created = client.post("/feedback", json=feedback_payload()).json()

    history = client.get("/feedback")

    assert history.status_code == 200
    body = history.json()
    assert body["total_records"] == 1
    assert body["records"][0]["record_id"] == created["record_id"]
    assert body["records"][0]["user_feedback"] == "correct"
    assert body["records"][0]["input_data"]["lead_time"] == 120

    update = client.patch(
        f"/feedback/{created['record_id']}",
        json={
            "user_feedback": "incorrect",
            "actual_status": "Not_Canceled",
            "comments": "Resultado corregido desde el histórico.",
        },
    )

    assert update.status_code == 200
    updated = update.json()
    assert updated["record_id"] == created["record_id"]
    assert updated["user_feedback"] == "incorrect"
    assert updated["actual_status"] == "Not_Canceled"
    assert updated["comments"] == "Resultado corregido desde el histórico."


def test_feedback_update_returns_not_found(feedback_database) -> None:
    response = client.patch(
        "/feedback/missing-record",
        json={
            "user_feedback": "unknown",
            "actual_status": None,
            "comments": None,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Feedback no encontrado."
