import pytest
from sqlalchemy.orm import sessionmaker

from app.backend.services import feedback_service
from src.data.database import Base, create_database_engine


@pytest.fixture
def feedback_database(tmp_path, monkeypatch):
    database_url = f"sqlite:///{(tmp_path / 'hotel_insights_test.db').as_posix()}"
    database_engine = create_database_engine(database_url)
    Base.metadata.create_all(bind=database_engine)
    session_factory = sessionmaker(
        bind=database_engine,
        autoflush=False,
        expire_on_commit=False,
    )
    monkeypatch.setattr(feedback_service, "SessionLocal", session_factory)

    yield database_url, session_factory

    database_engine.dispose()
