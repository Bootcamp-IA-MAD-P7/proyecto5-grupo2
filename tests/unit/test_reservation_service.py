import pandas as pd
import pytest

from app.backend.services import reservation_service


def reservation_row(booking_id: str, *, lead_time: int) -> dict:
    return {
        "Booking_ID": booking_id,
        "lead_time": lead_time,
        "arrival_year": 2018,
        "arrival_month": 7,
        "arrival_date": 15,
        "no_of_special_requests": 0,
        "avg_price_per_room": 100.0,
        "market_segment_type": "Online",
        "no_of_weekend_nights": 1,
        "no_of_week_nights": 2,
        "type_of_meal_plan": "Meal Plan 1",
        "room_type_reserved": "Room_Type 1",
        "no_of_adults": 2,
        "no_of_children": 0,
        "required_car_parking_space": 0,
        "repeated_guest": 0,
        "no_of_previous_cancellations": 0,
        "no_of_previous_bookings_not_canceled": 0,
    }


@pytest.fixture
def prioritized_dataset(monkeypatch):
    dataset = pd.DataFrame(
        [
            reservation_row("INN00002", lead_time=200),
            reservation_row("INN00003", lead_time=10),
            reservation_row("INN00001", lead_time=200),
        ]
    )
    load_calls = 0

    def load_dataset() -> pd.DataFrame:
        nonlocal load_calls
        load_calls += 1
        return dataset

    monkeypatch.setattr(reservation_service, "load_reservations_dataset", load_dataset)
    reservation_service.load_prioritized_reservations_dataset.cache_clear()
    reservation_service.load_reservations_by_id.cache_clear()
    yield lambda: load_calls
    reservation_service.load_prioritized_reservations_dataset.cache_clear()
    reservation_service.load_reservations_by_id.cache_clear()


def test_reservation_pages_are_ranked_deterministically(prioritized_dataset) -> None:
    first_page = reservation_service.get_demo_reservations(limit=1, offset=0)
    second_page = reservation_service.get_demo_reservations(limit=1, offset=1)

    assert first_page.reservations[0].id == "INN00001"
    assert second_page.reservations[0].id == "INN00002"
    assert first_page.has_more is True
    assert second_page.has_more is True
    assert prioritized_dataset() == 1


def test_reservation_page_after_end_is_empty(prioritized_dataset) -> None:
    page = reservation_service.get_demo_reservations(limit=2, offset=3)

    assert page.total_available == 3
    assert page.returned == 0
    assert page.offset == 3
    assert page.has_more is False
    assert page.reservations == []


def test_reservation_can_be_loaded_directly_by_booking_id(prioritized_dataset) -> None:
    reservation = reservation_service.get_demo_reservation_by_id("INN00003")

    assert reservation is not None
    assert reservation.id == "INN00003"
    assert reservation.input_data.lead_time == 10
    assert reservation_service.get_demo_reservation_by_id("INN99999") is None
    assert prioritized_dataset() == 1
