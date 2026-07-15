from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from src.data.database import Base, create_database_engine
from src.data.models import PredictionFeedback


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_CONFIG_PATH = PROJECT_ROOT / "alembic.ini"
MIGRATION_REVISION = "0001_prediction_feedback"


def run_upgrade(database_url: str, monkeypatch) -> Config:
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config(str(ALEMBIC_CONFIG_PATH))
    command.upgrade(config, "head")
    return config


def test_initial_migration_creates_versioned_schema(tmp_path, monkeypatch) -> None:
    database_url = f"sqlite:///{(tmp_path / 'new.db').as_posix()}"

    run_upgrade(database_url, monkeypatch)

    engine = create_database_engine(database_url)
    inspector = inspect(engine)
    assert {"alembic_version", "prediction_feedback"}.issubset(
        inspector.get_table_names()
    )
    assert {index["name"] for index in inspector.get_indexes("prediction_feedback")} == {
        "ix_prediction_feedback_actual_status",
        "ix_prediction_feedback_model_version",
        "ix_prediction_feedback_user_feedback",
    }
    with engine.connect() as connection:
        revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
    assert revision == MIGRATION_REVISION
    engine.dispose()


def test_initial_migration_adopts_legacy_table_without_data_loss(
    tmp_path,
    monkeypatch,
) -> None:
    database_url = f"sqlite:///{(tmp_path / 'legacy.db').as_posix()}"
    engine = create_database_engine(database_url)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        session.add(
            PredictionFeedback(
                record_id="legacy-record",
                model_version="random_forest_champion_v0.1.0",
                prediction="Canceled",
                probability=0.82,
                risk_level="high",
                user_feedback="correct",
                actual_status="Canceled",
                source="migration_test",
                comments=None,
                input_data={"lead_time": 120},
            )
        )
        session.commit()

    run_upgrade(database_url, monkeypatch)

    with engine.connect() as connection:
        record_count = connection.scalar(
            select(text("COUNT(*)")).select_from(text("prediction_feedback"))
        )
        revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
    assert record_count == 1
    assert revision == MIGRATION_REVISION
    engine.dispose()


def test_initial_migration_rejects_incompatible_legacy_schema(
    tmp_path,
    monkeypatch,
) -> None:
    database_url = f"sqlite:///{(tmp_path / 'invalid.db').as_posix()}"
    engine = create_database_engine(database_url)
    with engine.begin() as connection:
        connection.execute(
            text("CREATE TABLE prediction_feedback (record_id VARCHAR(36) PRIMARY KEY)")
        )
    engine.dispose()

    with pytest.raises(RuntimeError, match="does not match the Alembic baseline"):
        run_upgrade(database_url, monkeypatch)


def test_initial_migration_can_downgrade_temporary_schema(
    tmp_path,
    monkeypatch,
) -> None:
    database_url = f"sqlite:///{(tmp_path / 'downgrade.db').as_posix()}"
    config = run_upgrade(database_url, monkeypatch)

    command.downgrade(config, "base")

    engine = create_database_engine(database_url)
    assert "prediction_feedback" not in inspect(engine).get_table_names()
    engine.dispose()
