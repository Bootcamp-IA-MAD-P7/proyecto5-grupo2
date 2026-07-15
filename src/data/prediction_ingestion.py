"""Read audited prediction inputs for operational monitoring."""

from __future__ import annotations

import pandas as pd
from sqlalchemy import inspect, select

from src.data.database import create_database_engine, engine
from src.data.models import PredictionLog


DRIFT_SAMPLE_LIMIT = 1000
DRIFT_EXCLUDED_SOURCES = ("frontend_demo_queue", "prediction_api")


def load_prediction_records(
    database_url: str | None = None,
    *,
    limit: int = DRIFT_SAMPLE_LIMIT,
    excluded_sources: tuple[str, ...] = DRIFT_EXCLUDED_SOURCES,
) -> pd.DataFrame:
    """Load the most recent operational predictions eligible for drift checks."""

    if limit < 1:
        raise ValueError("Prediction sample limit must be greater than zero")

    database_engine = create_database_engine(database_url) if database_url else engine
    owns_engine = database_url is not None

    try:
        if not inspect(database_engine).has_table(PredictionLog.__tablename__):
            return pd.DataFrame()

        statement = select(PredictionLog)
        if excluded_sources:
            statement = statement.where(PredictionLog.source.not_in(excluded_sources))
        statement = statement.order_by(PredictionLog.created_at.desc()).limit(limit)

        with database_engine.connect() as connection:
            return pd.read_sql(statement, connection)
    finally:
        if owns_engine:
            database_engine.dispose()
