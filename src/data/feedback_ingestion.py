"""Utilities to reuse prediction feedback as future retraining data."""

from __future__ import annotations

import pandas as pd
from sqlalchemy import inspect, select

from src.data.database import create_database_engine, engine
from src.data.models import PredictionFeedback
from src.features.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN


def load_feedback_records(database_url: str | None = None) -> pd.DataFrame:
    """Load raw feedback records collected by the API."""

    database_engine = create_database_engine(database_url) if database_url else engine
    owns_engine = database_url is not None

    try:
        if not inspect(database_engine).has_table(PredictionFeedback.__tablename__):
            return pd.DataFrame()

        statement = select(PredictionFeedback)
        with database_engine.connect() as connection:
            return pd.read_sql(statement, connection)
    finally:
        if owns_engine:
            database_engine.dispose()


def build_retraining_dataset(database_url: str | None = None) -> pd.DataFrame:
    """Build a model-ready dataset from feedback rows with known real outcome."""

    feedback = load_feedback_records(database_url)
    if feedback.empty:
        return pd.DataFrame(columns=FEATURE_COLUMNS + [TARGET_COLUMN])

    labeled_feedback = feedback[feedback["actual_status"].isin(["Canceled", "Not_Canceled"])].copy()
    if labeled_feedback.empty:
        return pd.DataFrame(columns=FEATURE_COLUMNS + [TARGET_COLUMN])

    rows = []
    for _, record in labeled_feedback.iterrows():
        input_data = record["input_data"]
        row = {column: input_data[column] for column in FEATURE_COLUMNS}
        row[TARGET_COLUMN] = record["actual_status"]
        rows.append(row)

    return pd.DataFrame(rows, columns=FEATURE_COLUMNS + [TARGET_COLUMN])
