"""Train a reproducible neural-network challenger without touching the final holdout."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.utils.class_weight import compute_sample_weight

from src.evaluation.classification_metrics import (
    evaluate_classification,
    metrics_to_dataframe,
)
from src.features.preprocessing import (
    PROJECT_ROOT,
    DataSplits,
    build_preprocessor,
    load_dataset,
    prepare_data_splits,
)


RANDOM_STATE = 42
MODEL_NAME = "mlp_neural_network_challenger"
MODEL_PATH = PROJECT_ROOT / "models" / "challengers" / f"{MODEL_NAME}.pkl"
RESULT_PATH = PROJECT_ROOT / "reports" / "neural_network_experiment.json"
CHAMPION_METADATA_PATH = PROJECT_ROOT / "models" / "champion" / "champion_metadata.json"

NEURAL_NETWORK_PARAMS = {
    "hidden_layer_sizes": (64, 32),
    "activation": "relu",
    "solver": "adam",
    "alpha": 0.001,
    "batch_size": 256,
    "learning_rate_init": 0.001,
    "max_iter": 250,
    "early_stopping": True,
    "validation_fraction": 0.1,
    "n_iter_no_change": 15,
    "random_state": RANDOM_STATE,
}


def build_neural_network_challenger() -> Pipeline:
    """Build the experimental MLP with the shared preprocessing contract."""

    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(scale_numeric=True)),
            ("model", MLPClassifier(**NEURAL_NETWORK_PARAMS)),
        ]
    )


def train_and_evaluate_neural_network() -> tuple[pd.DataFrame, Pipeline, DataSplits]:
    """Fit on train and evaluate on train/validation only."""

    splits = prepare_data_splits(load_dataset())
    model = build_neural_network_challenger()
    sample_weight = compute_sample_weight(class_weight="balanced", y=splits.y_train)
    model.fit(
        splits.X_train,
        splits.y_train,
        model__sample_weight=sample_weight,
    )

    metrics = []
    for split_name, X_split, y_split in [
        ("train", splits.X_train, splits.y_train),
        ("validation", splits.X_validation, splits.y_validation),
    ]:
        metrics.append(
            evaluate_classification(
                model_name=MODEL_NAME,
                split=split_name,
                y_true=y_split,
                y_pred=model.predict(X_split),
                y_score=model.predict_proba(X_split)[:, 1],
            )
        )

    return metrics_to_dataframe(metrics), model, splits


def build_experiment_result(metrics_df: pd.DataFrame, model: Pipeline) -> dict:
    """Create the machine-readable comparison without promotion side effects."""

    train_metrics = metrics_df.loc[metrics_df["split"] == "train"].iloc[0]
    validation_metrics = metrics_df.loc[metrics_df["split"] == "validation"].iloc[0]
    f1_gap = float(
        abs(train_metrics["f1_canceled"] - validation_metrics["f1_canceled"])
    )

    champion_metadata = json.loads(CHAMPION_METADATA_PATH.read_text(encoding="utf-8"))
    champion_validation = champion_metadata["champion_validation_metrics"]
    champion_f1 = float(champion_validation["f1_canceled"])
    validation_f1 = float(validation_metrics["f1_canceled"])
    improves_champion = bool(validation_f1 > champion_f1)
    passes_overfitting = bool(f1_gap < 0.05)

    return {
        "experiment": MODEL_NAME,
        "model_type": type(model.named_steps["model"]).__name__,
        "random_state": RANDOM_STATE,
        "split_policy": {
            "training": "train",
            "evaluation": "validation",
            "final_test_used": False,
        },
        "class_balance": "balanced sample weights on training rows",
        "hyperparameters": {
            **NEURAL_NETWORK_PARAMS,
            "hidden_layer_sizes": list(NEURAL_NETWORK_PARAMS["hidden_layer_sizes"]),
        },
        "training_iterations": int(model.named_steps["model"].n_iter_),
        "metrics": {
            "train": _metric_record(train_metrics),
            "validation": _metric_record(validation_metrics),
        },
        "comparison": {
            "champion_model_version": champion_metadata["model_version"],
            "champion_validation_f1_canceled": champion_f1,
            "challenger_validation_f1_canceled": validation_f1,
            "f1_difference_vs_champion": validation_f1 - champion_f1,
            "train_validation_f1_gap": f1_gap,
            "passes_under_5_percent_overfitting_rule": passes_overfitting,
            "improves_champion_f1": improves_champion,
        },
        "decision": (
            "eligible_for_controlled_comparison"
            if improves_champion and passes_overfitting
            else "retain_champion"
        ),
        "notes": [
            "The final test split remains closed and was not used.",
            "This experiment never replaces or modifies the deployed Champion.",
        ],
    }


def save_experiment(model: Pipeline, result: dict) -> None:
    """Persist the challenger and its reproducible result."""

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MODEL_PATH.open("wb") as file:
        pickle.dump(model, file)
    RESULT_PATH.write_text(
        json.dumps(result, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _metric_record(row: pd.Series) -> dict:
    metric_fields = [
        "model_name",
        "split",
        "accuracy",
        "precision_canceled",
        "recall_canceled",
        "f1_canceled",
        "roc_auc",
        "true_negative",
        "false_positive",
        "false_negative",
        "true_positive",
    ]
    record = {field: row[field] for field in metric_fields}
    for field in ["true_negative", "false_positive", "false_negative", "true_positive"]:
        record[field] = int(record[field])
    for field in ["accuracy", "precision_canceled", "recall_canceled", "f1_canceled", "roc_auc"]:
        record[field] = float(record[field])
    return record


def main() -> None:
    metrics_df, model, _ = train_and_evaluate_neural_network()
    result = build_experiment_result(metrics_df, model)
    save_experiment(model, result)

    print(json.dumps(result, indent=2, ensure_ascii=True))
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Result saved to: {RESULT_PATH}")


if __name__ == "__main__":
    main()
