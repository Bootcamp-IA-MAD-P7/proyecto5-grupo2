"""Reusable preprocessing contract for the hotel reservations dataset."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "hotel-reservations-classification-dataset"
    / "Hotel Reservations.csv"
)

TARGET_COLUMN = "booking_status"
TARGET_MAPPING = {
    "Not_Canceled": 0,
    "Canceled": 1,
}

ID_COLUMNS = ["Booking_ID"]

NUMERIC_COLUMNS = [
    "no_of_adults",
    "no_of_children",
    "no_of_weekend_nights",
    "no_of_week_nights",
    "lead_time",
    "arrival_year",
    "arrival_month",
    "arrival_date",
    "no_of_previous_cancellations",
    "no_of_previous_bookings_not_canceled",
    "avg_price_per_room",
    "no_of_special_requests",
]

CATEGORICAL_COLUMNS = [
    "type_of_meal_plan",
    "room_type_reserved",
    "market_segment_type",
]

BINARY_COLUMNS = [
    "required_car_parking_space",
    "repeated_guest",
]

FEATURE_COLUMNS = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS + BINARY_COLUMNS
REQUIRED_COLUMNS = ID_COLUMNS + FEATURE_COLUMNS + [TARGET_COLUMN]


@dataclass(frozen=True)
class DataSplits:
    """Train, validation, and test splits before model fitting."""

    X_train: pd.DataFrame
    X_validation: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_validation: pd.Series
    y_test: pd.Series


def load_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    """Load the raw hotel reservations CSV."""

    return pd.read_csv(path)


def validate_required_columns(df: pd.DataFrame) -> None:
    """Fail early if the raw dataframe does not match the expected contract."""

    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def make_features_and_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separate model features from the binary target."""

    validate_required_columns(df)

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].map(TARGET_MAPPING)

    if y.isna().any():
        unknown_classes = sorted(set(df[TARGET_COLUMN]) - set(TARGET_MAPPING))
        raise ValueError(f"Unknown target classes: {unknown_classes}")

    return X, y.astype(int)


def split_train_validation_test(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    test_size: float = 0.15,
    validation_size: float = 0.15,
    random_state: int = 42,
) -> DataSplits:
    """Create stratified train, validation, and test splits."""

    if test_size <= 0 or validation_size <= 0:
        raise ValueError("test_size and validation_size must be greater than 0")
    if test_size + validation_size >= 1:
        raise ValueError("test_size + validation_size must be lower than 1")

    X_train_validation, X_test, y_train_validation, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    validation_relative_size = validation_size / (1 - test_size)
    X_train, X_validation, y_train, y_validation = train_test_split(
        X_train_validation,
        y_train_validation,
        test_size=validation_relative_size,
        random_state=random_state,
        stratify=y_train_validation,
    )

    return DataSplits(
        X_train=X_train,
        X_validation=X_validation,
        X_test=X_test,
        y_train=y_train,
        y_validation=y_validation,
        y_test=y_test,
    )


def build_preprocessor(*, scale_numeric: bool = True) -> ColumnTransformer:
    """Build the preprocessing transformer used before baseline training."""

    numeric_transformer = StandardScaler() if scale_numeric else "passthrough"
    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False,
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_COLUMNS),
            ("categorical", categorical_transformer, CATEGORICAL_COLUMNS),
            ("binary", "passthrough", BINARY_COLUMNS),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def prepare_data_splits(df: pd.DataFrame) -> DataSplits:
    """Prepare features, target, and stratified splits from a raw dataframe."""

    X, y = make_features_and_target(df)
    return split_train_validation_test(X, y)
