from uuid import UUID

from app.backend.observability import build_log_event, resolve_request_id


def test_resolve_request_id_preserves_safe_identifier() -> None:
    assert resolve_request_id("client-request_123") == "client-request_123"


def test_resolve_request_id_replaces_unsafe_identifier() -> None:
    request_id = resolve_request_id("unsafe request\nvalue")

    assert str(UUID(request_id)) == request_id


def test_log_event_contains_operational_metadata_only() -> None:
    event = build_log_event(
        "request_completed",
        request_id="request-123",
        method="POST",
        path="/predict",
        status_code=200,
        duration_ms=12.4,
    )

    assert event["service"] == "hotel-insights-api"
    assert event["event"] == "request_completed"
    assert event["request_id"] == "request-123"
    assert "payload" not in event
    assert "credentials" not in event
