from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.backend.schemas import DemoReservationResponse, DemoReservationsResponse, PredictionRequest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "hotel-reservations-classification-dataset"
    / "Hotel Reservations.csv"
)

FEATURE_COLUMNS = [
    "lead_time",
    "arrival_year",
    "arrival_month",
    "arrival_date",
    "no_of_special_requests",
    "avg_price_per_room",
    "market_segment_type",
    "no_of_weekend_nights",
    "no_of_week_nights",
    "type_of_meal_plan",
    "room_type_reserved",
    "no_of_adults",
    "no_of_children",
    "required_car_parking_space",
    "repeated_guest",
    "no_of_previous_cancellations",
    "no_of_previous_bookings_not_canceled",
]

IMAGE_KEYS = ["terrace", "suite", "pool", "lobby", "garden"]
ROOM_LABELS = {
    "Room_Type 1": "Habitacion clasica",
    "Room_Type 2": "Habitacion superior",
    "Room_Type 3": "Estancia familiar",
    "Room_Type 4": "Suite urbana",
    "Room_Type 5": "Suite wellness",
    "Room_Type 6": "Suite familiar",
    "Room_Type 7": "Suite premium",
}


@lru_cache(maxsize=1)
def load_reservations_dataset() -> pd.DataFrame:
    return pd.read_csv(DATASET_PATH)


def get_demo_reservations(limit: int = 8, offset: int = 0) -> DemoReservationsResponse:
    prioritized_dataset = load_prioritized_reservations_dataset()
    sample = prioritized_dataset.iloc[offset : offset + limit]

    reservations = [
        _to_demo_reservation(row, image_index=offset + index)
        for index, (_, row) in enumerate(sample.iterrows())
    ]
    total_available = int(len(prioritized_dataset))
    returned = len(reservations)

    return DemoReservationsResponse(
        total_available=total_available,
        returned=returned,
        limit=limit,
        offset=offset,
        has_more=offset + returned < total_available,
        source="data/raw/hotel-reservations-classification-dataset/Hotel Reservations.csv",
        reservations=reservations,
    )


def get_demo_reservation_by_id(booking_id: str) -> DemoReservationResponse | None:
    reservations_by_id = load_reservations_by_id()
    if booking_id not in reservations_by_id.index:
        return None

    row = reservations_by_id.loc[booking_id]
    image_index = sum(ord(character) for character in booking_id)
    return _to_demo_reservation(row, image_index=image_index)


@lru_cache(maxsize=1)
def load_prioritized_reservations_dataset() -> pd.DataFrame:
    candidates = load_reservations_dataset().copy()
    candidates["estimated_value"] = (
        candidates["avg_price_per_room"]
        * (candidates["no_of_weekend_nights"] + candidates["no_of_week_nights"]).clip(lower=1)
    )
    candidates["priority_score"] = (
        candidates["lead_time"].clip(upper=240) * 0.45
        + candidates["estimated_value"].clip(upper=1200) * 0.08
        + (candidates["no_of_special_requests"] == 0).astype(int) * 45
        + (candidates["market_segment_type"] == "Online").astype(int) * 28
        + candidates["no_of_previous_cancellations"].clip(upper=3) * 35
    )

    return candidates.sort_values(
        ["priority_score", "Booking_ID"],
        ascending=[False, True],
        kind="mergesort",
    )


@lru_cache(maxsize=1)
def load_reservations_by_id() -> pd.DataFrame:
    return (
        load_reservations_dataset()
        .drop_duplicates(subset="Booking_ID", keep="first")
        .set_index("Booking_ID", drop=False)
    )


def _to_demo_reservation(row: pd.Series, image_index: int) -> DemoReservationResponse:
    booking_id = str(row["Booking_ID"])
    return DemoReservationResponse(
        id=booking_id,
        display_name=f"Reserva {booking_id}",
        stay_label=_stay_label(row),
        status_label=_status_label(row),
        image_key=IMAGE_KEYS[image_index % len(IMAGE_KEYS)],
        input_data=PredictionRequest(**{column: row[column] for column in FEATURE_COLUMNS}),
    )


def _stay_label(row: pd.Series) -> str:
    nights = int(row["no_of_weekend_nights"] + row["no_of_week_nights"])
    room_type = ROOM_LABELS.get(str(row["room_type_reserved"]), str(row["room_type_reserved"]).replace("_", " "))
    return f"{room_type} · {nights} noches"


def _status_label(row: pd.Series) -> str:
    if int(row["no_of_previous_cancellations"]) > 0:
        return "Historial sensible"
    if int(row["lead_time"]) >= 120 and int(row["no_of_special_requests"]) == 0:
        return "Conviene confirmar"
    if int(row["repeated_guest"]) == 1:
        return "Cliente recurrente"
    if int(row["required_car_parking_space"]) == 1 or int(row["no_of_special_requests"]) > 0:
        return "Buena señal de viaje"
    return "Revision ligera"
