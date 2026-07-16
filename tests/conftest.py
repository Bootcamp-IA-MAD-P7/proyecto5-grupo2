import pytest
from sqlalchemy.orm import sessionmaker

from app.backend.services import feedback_service, health_service, prediction_log_service
from src.data.database import Base, create_database_engine


@pytest.fixture(autouse=True)
def operational_database(tmp_path, monkeypatch):
    database_url = f"sqlite:///{(tmp_path / 'hotel_insights_test.db').as_posix()}"
    database_engine = create_database_engine(database_url)
    Base.metadata.create_all(bind=database_engine)
    session_factory = sessionmaker(
        bind=database_engine,
        autoflush=False,
        expire_on_commit=False,
    )
    monkeypatch.setattr(feedback_service, "SessionLocal", session_factory)
    monkeypatch.setattr(health_service, "SessionLocal", session_factory)
    monkeypatch.setattr(prediction_log_service, "SessionLocal", session_factory)

    yield database_url, session_factory

    database_engine.dispose()


@pytest.fixture
def feedback_database(operational_database):
    """Backward-compatible fixture name for feedback-focused tests."""

    return operational_database
