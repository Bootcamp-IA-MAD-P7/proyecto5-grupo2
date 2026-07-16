"""Small structured-logging layer for API runtime observability."""

from __future__ import annotations

from datetime import UTC, datetime
import json
import logging
import re
import sys
from typing import Any
from uuid import uuid4


LOGGER_NAME = "hotel_insights.api"
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def _configure_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    return logger


logger = _configure_logger()


def resolve_request_id(candidate: str | None) -> str:
    """Reuse a safe caller identifier or generate a new UUID."""

    if candidate and REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate
    return str(uuid4())


def build_log_event(event: str, **fields: Any) -> dict[str, Any]:
    """Build a serialisable event without request payloads or credentials."""

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "hotel-insights-api",
        "event": event,
        **fields,
    }


def emit_log_event(event: str, *, level: int = logging.INFO, **fields: Any) -> None:
    logger.log(
        level,
        json.dumps(build_log_event(event, **fields), ensure_ascii=True, default=str),
    )
