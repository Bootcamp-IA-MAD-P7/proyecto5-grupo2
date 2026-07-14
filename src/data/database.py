"""Shared database configuration for operational application data."""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "data" / "app" / "hotel_insights.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"


class Base(DeclarativeBase):
    """Declarative base for operational database models."""


def normalize_database_url(database_url: str) -> str:
    """Use the psycopg SQLAlchemy driver for PostgreSQL URLs."""

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def create_database_engine(database_url: str) -> Engine:
    """Create an engine suitable for SQLite tests or PostgreSQL runtime."""

    normalized_url = normalize_database_url(database_url)
    connect_args = {}

    if normalized_url.startswith("sqlite:///"):
        sqlite_path = normalized_url.removeprefix("sqlite:///")
        if sqlite_path != ":memory:":
            Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        connect_args["check_same_thread"] = False

    return create_engine(
        normalized_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


def database_backend_name(database_url: str) -> str:
    """Return a safe backend name without exposing credentials."""

    normalized_url = normalize_database_url(database_url)
    return "postgresql" if normalized_url.startswith("postgresql+") else "sqlite"


DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
engine = create_database_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_database_schema() -> None:
    """Create missing tables for the current application schema."""

    from src.data import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
