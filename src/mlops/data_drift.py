"""Population Stability Index monitoring for model input features."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.features.preprocessing import (
    BINARY_COLUMNS,
    CATEGORICAL_COLUMNS,
    DATASET_PATH,
    FEATURE_COLUMNS,
    NUMERIC_COLUMNS,
    PROJECT_ROOT,
    load_dataset,
    prepare_data_splits,
)


PROFILE_PATH = PROJECT_ROOT / "models" / "monitoring" / "training_reference_profile.json"
PROFILE_VERSION = "training_reference_v1"
MINIMUM_CURRENT_ROWS = 100
MODERATE_DRIFT_THRESHOLD = 0.10
HIGH_DRIFT_THRESHOLD = 0.25
EPSILON = 1e-6
OTHER_CATEGORY = "__OTHER__"
MISSING_CATEGORY = "__MISSING__"
NUMERIC_QUANTILES = np.linspace(0.0, 1.0, 11)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalise_proportions(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values.astype(float), EPSILON, None)
    return clipped / clipped.sum()


def _numeric_profile(series: pd.Series) -> dict:
    values = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
    if values.size == 0:
        raise ValueError(f"Numeric feature {series.name!r} has no valid values")

    quantiles = np.quantile(values, NUMERIC_QUANTILES)
    interior_edges = np.unique(quantiles)[1:-1]
    bins = np.concatenate(([-np.inf], interior_edges, [np.inf]))
    counts, _ = np.histogram(values, bins=bins)
    proportions = counts / counts.sum()

    return {
        "feature_type": "numeric",
        "bin_edges": interior_edges.tolist(),
        "expected_proportions": proportions.tolist(),
    }


def _categorical_profile(series: pd.Series) -> dict:
    values = series.astype("string").fillna(MISSING_CATEGORY)
    proportions = values.value_counts(normalize=True, dropna=False).sort_index()

    return {
        "feature_type": "categorical",
        "expected_proportions": {
            str(category): float(proportion)
            for category, proportion in proportions.items()
        },
    }


def build_reference_profile(reference_features: pd.DataFrame) -> dict:
    """Build a stable training profile used by runtime drift checks."""

    missing_columns = sorted(set(FEATURE_COLUMNS) - set(reference_features.columns))
    if missing_columns:
        raise ValueError(f"Missing reference features: {missing_columns}")

    feature_profiles = {}
    for feature in NUMERIC_COLUMNS:
        feature_profiles[feature] = _numeric_profile(reference_features[feature])
    for feature in [*CATEGORICAL_COLUMNS, *BINARY_COLUMNS]:
        feature_profiles[feature] = _categorical_profile(reference_features[feature])

    return {
        "profile_version": PROFILE_VERSION,
        "created_at": datetime.now(UTC).isoformat(),
        "source": "stratified_training_split",
        "reference_rows": len(reference_features),
        "dataset_path": DATASET_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "dataset_sha256": _sha256_file(DATASET_PATH),
        "split": {
            "train_fraction": 0.70,
            "validation_fraction": 0.15,
            "test_fraction": 0.15,
            "random_state": 42,
            "stratified": True,
        },
        "thresholds": {
            "moderate": MODERATE_DRIFT_THRESHOLD,
            "high": HIGH_DRIFT_THRESHOLD,
            "minimum_current_rows": MINIMUM_CURRENT_ROWS,
        },
        "features": feature_profiles,
    }


def create_training_reference_profile() -> dict:
    """Reconstruct X_train and profile it without reading the closed test labels."""

    splits = prepare_data_splits(load_dataset())
    return build_reference_profile(splits.X_train)


def save_reference_profile(profile: dict, path: Path = PROFILE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(profile, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_reference_profile(path: Path = PROFILE_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def prediction_records_to_features(prediction_records: pd.DataFrame) -> pd.DataFrame:
    """Extract valid model inputs from persisted prediction audit rows."""

    if prediction_records.empty or "input_data" not in prediction_records.columns:
        return pd.DataFrame(columns=FEATURE_COLUMNS)

    rows = []
    for payload in prediction_records["input_data"]:
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                continue

        if not isinstance(payload, dict):
            continue
        if not all(feature in payload for feature in FEATURE_COLUMNS):
            continue

        rows.append({feature: payload[feature] for feature in FEATURE_COLUMNS})

    return pd.DataFrame(rows, columns=FEATURE_COLUMNS)


def _psi(expected: np.ndarray, current: np.ndarray) -> float:
    expected_distribution = _normalise_proportions(expected)
    current_distribution = _normalise_proportions(current)
    values = (current_distribution - expected_distribution) * np.log(
        current_distribution / expected_distribution
    )
    return float(values.sum())


def _numeric_psi(profile: dict, current_series: pd.Series) -> float:
    values = pd.to_numeric(current_series, errors="coerce").dropna().to_numpy(dtype=float)
    edges = np.asarray(profile["bin_edges"], dtype=float)
    bins = np.concatenate(([-np.inf], edges, [np.inf]))
    counts, _ = np.histogram(values, bins=bins)
    current = counts / counts.sum() if counts.sum() else np.zeros_like(counts, dtype=float)
    expected = np.asarray(profile["expected_proportions"], dtype=float)
    return _psi(expected, current)


def _categorical_psi(profile: dict, current_series: pd.Series) -> float:
    expected_mapping = profile["expected_proportions"]
    known_categories = set(expected_mapping)
    current_values = current_series.astype("string").fillna(MISSING_CATEGORY)
    current_values = current_values.map(
        lambda value: value if value in known_categories else OTHER_CATEGORY
    )
    categories = [*sorted(known_categories), OTHER_CATEGORY]
    current_mapping = current_values.value_counts(normalize=True, dropna=False)
    expected = np.asarray(
        [expected_mapping.get(category, 0.0) for category in categories],
        dtype=float,
    )
    current = np.asarray(
        [float(current_mapping.get(category, 0.0)) for category in categories],
        dtype=float,
    )
    return _psi(expected, current)


def _feature_status(psi_value: float) -> str:
    if psi_value >= HIGH_DRIFT_THRESHOLD:
        return "high"
    if psi_value >= MODERATE_DRIFT_THRESHOLD:
        return "moderate"
    return "stable"


def calculate_drift_report(
    reference_profile: dict,
    current_features: pd.DataFrame,
    *,
    minimum_current_rows: int = MINIMUM_CURRENT_ROWS,
) -> dict:
    """Compare current model inputs with the frozen training profile."""

    current_rows = len(current_features)
    base_report = {
        "profile_version": reference_profile["profile_version"],
        "generated_at": datetime.now(UTC).isoformat(),
        "reference_rows": int(reference_profile["reference_rows"]),
        "current_rows": current_rows,
        "minimum_current_rows": minimum_current_rows,
        "thresholds": {
            "moderate": MODERATE_DRIFT_THRESHOLD,
            "high": HIGH_DRIFT_THRESHOLD,
        },
    }

    if current_rows < minimum_current_rows:
        return {
            **base_report,
            "status": "insufficient_data",
            "max_psi": None,
            "drifted_features": [],
            "features": [],
            "message": (
                f"At least {minimum_current_rows} current records are required; "
                f"only {current_rows} are available."
            ),
        }

    missing_columns = sorted(set(FEATURE_COLUMNS) - set(current_features.columns))
    if missing_columns:
        raise ValueError(f"Missing current features: {missing_columns}")

    feature_results = []
    for feature in FEATURE_COLUMNS:
        feature_profile = reference_profile["features"][feature]
        if feature_profile["feature_type"] == "numeric":
            psi_value = _numeric_psi(feature_profile, current_features[feature])
        else:
            psi_value = _categorical_psi(feature_profile, current_features[feature])

        feature_results.append(
            {
                "feature": feature,
                "feature_type": feature_profile["feature_type"],
                "psi": psi_value,
                "status": _feature_status(psi_value),
            }
        )

    feature_results.sort(key=lambda item: item["psi"], reverse=True)
    high_features = [item["feature"] for item in feature_results if item["status"] == "high"]
    moderate_features = [
        item["feature"] for item in feature_results if item["status"] == "moderate"
    ]

    if high_features:
        status = "drift_detected"
        drifted_features = high_features
    elif moderate_features:
        status = "warning"
        drifted_features = moderate_features
    else:
        status = "stable"
        drifted_features = []

    return {
        **base_report,
        "status": status,
        "max_psi": feature_results[0]["psi"],
        "drifted_features": drifted_features,
        "features": feature_results,
        "message": (
            "Drift is an evaluation signal and never promotes a model automatically."
        ),
    }


def main() -> None:
    profile = create_training_reference_profile()
    save_reference_profile(profile)
    print(f"Training drift profile written to: {PROFILE_PATH}")


if __name__ == "__main__":
    main()
