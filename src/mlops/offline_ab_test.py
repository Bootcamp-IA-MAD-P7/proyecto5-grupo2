"""Run a deterministic offline A/B test without modifying production traffic."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

from src.evaluation.classification_metrics import evaluate_classification
from src.features.preprocessing import PROJECT_ROOT, load_dataset, prepare_data_splits


RANDOM_STATE = 42
CHALLENGER_SHARE = 0.20
BOOTSTRAP_ITERATIONS = 1000
EXPERIMENT_ID = "offline_ab_champion_vs_mlp_v1"

CHAMPION_MODEL_PATH = PROJECT_ROOT / "models" / "champion" / "random_forest_champion.pkl"
CHAMPION_METADATA_PATH = PROJECT_ROOT / "models" / "champion" / "champion_metadata.json"
CHALLENGER_MODEL_PATH = (
    PROJECT_ROOT / "models" / "challengers" / "mlp_neural_network_challenger.pkl"
)
CHALLENGER_RESULT_PATH = PROJECT_ROOT / "reports" / "neural_network_experiment.json"
RESULT_PATH = PROJECT_ROOT / "reports" / "offline_ab_test_results.json"
ASSIGNMENTS_PATH = PROJECT_ROOT / "reports" / "offline_ab_test_assignments.csv"


def assign_ab_arms(
    y_validation: pd.Series,
    *,
    challenger_share: float = CHALLENGER_SHARE,
    random_state: int = RANDOM_STATE,
) -> tuple[np.ndarray, np.ndarray]:
    """Return deterministic stratified positions for Champion and Challenger."""

    if not 0 < challenger_share < 1:
        raise ValueError("challenger_share must be between 0 and 1")

    positions = np.arange(len(y_validation))
    champion_positions, challenger_positions = train_test_split(
        positions,
        test_size=challenger_share,
        random_state=random_state,
        stratify=y_validation.to_numpy(),
    )
    return np.sort(champion_positions), np.sort(challenger_positions)


def run_offline_ab_test() -> tuple[dict, pd.DataFrame]:
    """Evaluate one model per validation row using an auditable 80/20 split."""

    dataset = load_dataset()
    splits = prepare_data_splits(dataset)
    champion_positions, challenger_positions = assign_ab_arms(splits.y_validation)

    champion = _load_pickle(CHAMPION_MODEL_PATH)
    challenger = _load_pickle(CHALLENGER_MODEL_PATH)
    champion_metadata = json.loads(CHAMPION_METADATA_PATH.read_text(encoding="utf-8"))
    challenger_result = json.loads(CHALLENGER_RESULT_PATH.read_text(encoding="utf-8"))

    champion_version = champion_metadata["model_version"]
    challenger_version = "mlp_neural_network_challenger_v0.1.0"

    champion_arm = _evaluate_arm(
        arm="A",
        model=champion,
        model_version=champion_version,
        positions=champion_positions,
        splits=splits,
        dataset=dataset,
    )
    challenger_arm = _evaluate_arm(
        arm="B",
        model=challenger,
        model_version=challenger_version,
        positions=challenger_positions,
        splits=splits,
        dataset=dataset,
    )

    assignments = pd.concat(
        [champion_arm["assignments"], challenger_arm["assignments"]],
        ignore_index=True,
    ).sort_values("source_row_index").reset_index(drop=True)

    champion_f1 = champion_arm["metrics"]["f1_canceled"]
    challenger_f1 = challenger_arm["metrics"]["f1_canceled"]
    difference = challenger_f1 - champion_f1
    confidence_interval = _bootstrap_f1_difference(
        champion_arm["assignments"],
        challenger_arm["assignments"],
    )
    challenger_wins = difference > 0 and confidence_interval[0] > 0

    result = {
        "experiment_id": EXPERIMENT_ID,
        "experiment_type": "offline_ab_simulation",
        "random_state": RANDOM_STATE,
        "split_policy": {
            "source": "validation",
            "final_test_used": False,
            "champion_share": 1 - CHALLENGER_SHARE,
            "challenger_share": CHALLENGER_SHARE,
            "stratified": True,
        },
        "primary_metric": "f1_canceled",
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "arms": {
            "A": _arm_result(champion_arm),
            "B": _arm_result(challenger_arm),
        },
        "cohort_balance": {
            "champion_positive_rate": champion_arm["positive_rate"],
            "challenger_positive_rate": challenger_arm["positive_rate"],
            "absolute_positive_rate_difference": abs(
                champion_arm["positive_rate"] - challenger_arm["positive_rate"]
            ),
        },
        "comparison": {
            "challenger_minus_champion_f1": difference,
            "bootstrap_95_percent_ci": {
                "lower": confidence_interval[0],
                "upper": confidence_interval[1],
            },
            "statistically_supported_challenger_win": challenger_wins,
        },
        "decision": "promote_challenger_candidate" if challenger_wins else "retain_champion",
        "artifacts": {
            "assignments": "reports/offline_ab_test_assignments.csv",
            "challenger_experiment": "reports/neural_network_experiment.json",
        },
        "notes": [
            "Each validation row is assigned to exactly one model.",
            "The simulation does not write predictions to the operational database.",
            "The final test split remains closed.",
            f"Neural-network prior decision: {challenger_result['decision']}.",
        ],
    }
    return result, assignments


def save_ab_test(result: dict, assignments: pd.DataFrame) -> None:
    """Persist the experiment summary and row-level audit evidence."""

    RESULT_PATH.write_text(
        json.dumps(result, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    assignments.to_csv(ASSIGNMENTS_PATH, index=False)


def _evaluate_arm(*, arm, model, model_version, positions, splits, dataset) -> dict:
    X_arm = splits.X_validation.iloc[positions]
    y_arm = splits.y_validation.iloc[positions]
    predictions = model.predict(X_arm)
    probabilities = model.predict_proba(X_arm)[:, 1]
    metrics = evaluate_classification(
        model_name=model_version,
        split=f"validation_arm_{arm.lower()}",
        y_true=y_arm,
        y_pred=predictions,
        y_score=probabilities,
    )

    source_indices = X_arm.index.to_numpy()
    booking_ids = dataset.loc[source_indices, "Booking_ID"].astype(str).to_numpy()
    assignments = pd.DataFrame(
        {
            "experiment_id": EXPERIMENT_ID,
            "prediction_id": [
                str(uuid5(NAMESPACE_URL, f"{EXPERIMENT_ID}:{booking_id}:{arm}"))
                for booking_id in booking_ids
            ],
            "source_row_index": source_indices,
            "booking_id": booking_ids,
            "arm": arm,
            "model_version": model_version,
            "actual_label": y_arm.to_numpy(),
            "predicted_label": predictions,
            "canceled_probability": probabilities,
        }
    )
    return {
        "arm": arm,
        "model_version": model_version,
        "rows": len(assignments),
        "positive_rate": float(y_arm.mean()),
        "metrics": _metrics_to_dict(metrics),
        "assignments": assignments,
    }


def _bootstrap_f1_difference(
    champion_assignments: pd.DataFrame,
    challenger_assignments: pd.DataFrame,
) -> tuple[float, float]:
    rng = np.random.default_rng(RANDOM_STATE)
    differences = np.empty(BOOTSTRAP_ITERATIONS)

    for iteration in range(BOOTSTRAP_ITERATIONS):
        champion_sample = champion_assignments.iloc[
            rng.integers(0, len(champion_assignments), len(champion_assignments))
        ]
        challenger_sample = challenger_assignments.iloc[
            rng.integers(0, len(challenger_assignments), len(challenger_assignments))
        ]
        champion_f1 = f1_score(
            champion_sample["actual_label"],
            champion_sample["predicted_label"],
            zero_division=0,
        )
        challenger_f1 = f1_score(
            challenger_sample["actual_label"],
            challenger_sample["predicted_label"],
            zero_division=0,
        )
        differences[iteration] = challenger_f1 - champion_f1

    lower, upper = np.percentile(differences, [2.5, 97.5])
    return float(lower), float(upper)


def _metrics_to_dict(metrics) -> dict:
    return {
        "accuracy": float(metrics.accuracy),
        "precision_canceled": float(metrics.precision_canceled),
        "recall_canceled": float(metrics.recall_canceled),
        "f1_canceled": float(metrics.f1_canceled),
        "roc_auc": float(metrics.roc_auc),
        "true_negative": metrics.true_negative,
        "false_positive": metrics.false_positive,
        "false_negative": metrics.false_negative,
        "true_positive": metrics.true_positive,
    }


def _arm_result(arm: dict) -> dict:
    return {
        "model_version": arm["model_version"],
        "rows": arm["rows"],
        "positive_rate": arm["positive_rate"],
        "metrics": arm["metrics"],
    }


def _load_pickle(path: Path):
    with path.open("rb") as file:
        return pickle.load(file)


def main() -> None:
    result, assignments = run_offline_ab_test()
    save_ab_test(result, assignments)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    print(f"Assignments saved to: {ASSIGNMENTS_PATH}")
    print(f"Result saved to: {RESULT_PATH}")


if __name__ == "__main__":
    main()
