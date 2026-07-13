import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.backend.schemas import FeedbackRequest, FeedbackResponse, FeedbackSummaryResponse


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FEEDBACK_FILE = PROJECT_ROOT / "data" / "feedback" / "prediction_feedback.csv"

FIELDNAMES = [
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


def save_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    record_id = str(uuid4())
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    file_exists = FEEDBACK_FILE.exists()

    row = {
        "record_id": record_id,
        "created_at": datetime.now(UTC).isoformat(),
        "model_version": payload.model_version,
        "prediction": payload.prediction,
        "probability": payload.probability,
        "risk_level": payload.risk_level,
        "user_feedback": payload.user_feedback,
        "actual_status": payload.actual_status or "",
        "source": payload.source,
        "comments": payload.comments or "",
        "input_json": json.dumps(payload.input_data.model_dump(), ensure_ascii=True, sort_keys=True),
    }

    with FEEDBACK_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    return FeedbackResponse(status="stored", record_id=record_id, stored=True)


def get_feedback_summary() -> FeedbackSummaryResponse:
    if not FEEDBACK_FILE.exists():
        return FeedbackSummaryResponse(total_records=0, storage=str(FEEDBACK_FILE))

    with FEEDBACK_FILE.open(encoding="utf-8") as file:
        total_records = max(sum(1 for _ in file) - 1, 0)

    return FeedbackSummaryResponse(total_records=total_records, storage=str(FEEDBACK_FILE))
