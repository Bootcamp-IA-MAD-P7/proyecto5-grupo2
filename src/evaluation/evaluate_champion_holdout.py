"""Run and record the one-time final Champion holdout evaluation."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
import hashlib
import json
import pickle
from pathlib import Path

from src.evaluation.classification_metrics import evaluate_classification
from src.features.preprocessing import DATASET_PATH, PROJECT_ROOT, load_dataset, prepare_data_splits


METADATA_PATH = PROJECT_ROOT / "models" / "champion" / "champion_metadata.json"
RESULT_PATH = PROJECT_ROOT / "reports" / "champion_test_metrics.json"
MIN_TEST_F1_CANCELED = 0.80
MAX_VALIDATION_TEST_F1_GAP = 0.05
RANDOM_STATE = 42
TEST_SIZE = 0.15
VALIDATION_SIZE = 0.15


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for a reproducibility-critical artifact."""

    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evaluate_acceptance(metrics: dict, validation_f1: float) -> dict:
    """Apply the acceptance criteria declared before opening the holdout."""

    test_f1 = float(metrics["f1_canceled"])
    validation_test_gap = abs(float(validation_f1) - test_f1)
    passes_f1 = test_f1 >= MIN_TEST_F1_CANCELED
    passes_gap = validation_test_gap <= MAX_VALIDATION_TEST_F1_GAP

    return {
        "minimum_f1_canceled": MIN_TEST_F1_CANCELED,
        "maximum_validation_test_f1_gap": MAX_VALIDATION_TEST_F1_GAP,
        "validation_test_f1_gap": validation_test_gap,
        "passes_minimum_f1": passes_f1,
        "passes_stability_gap": passes_gap,
        "passes_all_criteria": passes_f1 and passes_gap,
    }


def evaluate_champion_holdout() -> dict:
    """Evaluate the frozen Champion on the reserved test split only."""

    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    model_path = PROJECT_ROOT / metadata["champion_artifact"]

    with model_path.open("rb") as file:
        model = pickle.load(file)

    dataset = load_dataset()
    splits = prepare_data_splits(dataset)
    y_pred = model.predict(splits.X_test)
    y_score = model.predict_proba(splits.X_test)[:, 1]
    metrics = evaluate_classification(
        model_name="random_forest_champion",
        split="test",
        y_true=splits.y_test,
        y_pred=y_pred,
        y_score=y_score,
    )
    metrics_dict = asdict(metrics)
    validation_f1 = metadata["champion_validation_metrics"]["f1_canceled"]

    return {
        "evaluation_status": "completed",
        "evaluation_date": date.today().isoformat(),
        "one_time_holdout": True,
        "model_version": metadata["model_version"],
        "model_artifact": metadata["champion_artifact"],
        "model_sha256": sha256_file(model_path),
        "dataset_path": DATASET_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "dataset_sha256": sha256_file(DATASET_PATH),
        "split_strategy": {
            "train_fraction": 0.70,
            "validation_fraction": VALIDATION_SIZE,
            "test_fraction": TEST_SIZE,
            "random_state": RANDOM_STATE,
            "stratified": True,
            "train_rows": len(splits.X_train),
            "validation_rows": len(splits.X_validation),
            "test_rows": len(splits.X_test),
        },
        "metrics": metrics_dict,
        "acceptance": evaluate_acceptance(metrics_dict, validation_f1),
        "policy": (
            "The Champion remains frozen after this evaluation. Test results "
            "must not be used for further model tuning."
        ),
    }


def record_holdout_evaluation(
    result: dict,
    *,
    metadata_path: Path = METADATA_PATH,
    result_path: Path = RESULT_PATH,
) -> None:
    """Persist the holdout result once and update Champion metadata."""

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if result_path.exists() or "champion_test_metrics" in metadata:
        raise RuntimeError("The final Champion holdout has already been recorded")

    metadata["champion_test_metrics"] = result["metrics"]
    metadata["final_holdout_evaluation"] = {
        "evaluation_date": result["evaluation_date"],
        "result_artifact": result_path.relative_to(PROJECT_ROOT).as_posix()
        if result_path.is_relative_to(PROJECT_ROOT)
        else result_path.as_posix(),
        "model_sha256": result["model_sha256"],
        "dataset_sha256": result["dataset_sha256"],
        "split_strategy": result["split_strategy"],
        "acceptance": result["acceptance"],
        "policy": result["policy"],
    }
    metadata["limitations"] = [
        limitation
        for limitation in metadata.get("limitations", [])
        if "test split remains reserved" not in limitation.lower()
    ]
    metadata["limitations"].append(
        "The reserved test split was evaluated once and is closed for further tuning."
    )

    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    if RESULT_PATH.exists():
        raise RuntimeError("The final Champion holdout has already been evaluated")

    result = evaluate_champion_holdout()
    record_holdout_evaluation(result)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
