"""Utilities to reuse prediction feedback as future retraining data."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.features.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FEEDBACK_FILE = PROJECT_ROOT / "data" / "feedback" / "prediction_feedback.csv"


def load_feedback_records(feedback_file: Path = DEFAULT_FEEDBACK_FILE) -> pd.DataFrame:
    """Load raw feedback records collected by the API."""

    if not feedback_file.exists():
        return pd.DataFrame()

    return pd.read_csv(feedback_file)


def build_retraining_dataset(feedback_file: Path = DEFAULT_FEEDBACK_FILE) -> pd.DataFrame:
    """Build a model-ready dataset from feedback rows with known real outcome."""

    feedback = load_feedback_records(feedback_file)
    if feedback.empty:
        return pd.DataFrame(columns=FEATURE_COLUMNS + [TARGET_COLUMN])

    labeled_feedback = feedback[feedback["actual_status"].isin(["Canceled", "Not_Canceled"])].copy()
    if labeled_feedback.empty:
        return pd.DataFrame(columns=FEATURE_COLUMNS + [TARGET_COLUMN])

    rows = []
    for _, record in labeled_feedback.iterrows():
        input_data = json.loads(record["input_json"])
        row = {column: input_data[column] for column in FEATURE_COLUMNS}
        row[TARGET_COLUMN] = record["actual_status"]
        rows.append(row)

    return pd.DataFrame(rows, columns=FEATURE_COLUMNS + [TARGET_COLUMN])
