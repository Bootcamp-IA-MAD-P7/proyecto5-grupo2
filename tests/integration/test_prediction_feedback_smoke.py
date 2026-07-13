from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.services import feedback_service
from tests.test_backend_api import valid_prediction_payload


client = TestClient(app)


def test_prediction_feedback_smoke_flow(tmp_path, monkeypatch) -> None:
    feedback_file = tmp_path / "prediction_feedback.csv"
    monkeypatch.setattr(feedback_service, "FEEDBACK_FILE", feedback_file)

    health = client.get("/health")
    assert health.status_code == 200

    model_info = client.get("/model/info")
    assert model_info.status_code == 200
    assert model_info.json()["model_version"] == "random_forest_champion_v0.1.0"

    prediction = client.post("/predict", json=valid_prediction_payload())
    assert prediction.status_code == 200
    prediction_body = prediction.json()

    feedback_payload = {
        "input_data": valid_prediction_payload(),
        "prediction": prediction_body["prediction"],
        "probability": prediction_body["probability"],
        "risk_level": prediction_body["risk_level"],
        "model_version": prediction_body["model_version"],
        "user_feedback": "unknown",
        "actual_status": None,
        "comments": "End-to-end smoke validation.",
        "source": "smoke_test",
    }

    feedback = client.post("/feedback", json=feedback_payload)
    assert feedback.status_code == 200
    assert feedback.json()["stored"] is True

    summary = client.get("/feedback/summary")
    assert summary.status_code == 200
    assert summary.json()["total_records"] == 1
