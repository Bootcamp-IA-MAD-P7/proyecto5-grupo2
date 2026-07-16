"""Evaluate and optionally apply a guarded Champion model promotion."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
import shutil
from copy import deepcopy
from datetime import date
from pathlib import Path

from src.features.preprocessing import PROJECT_ROOT


MIN_F1_IMPROVEMENT = 0.02
MAX_OVERFITTING_GAP = 0.05
MAX_CRITICAL_METRIC_DEGRADATION = 0.02

CHAMPION_MODEL_PATH = PROJECT_ROOT / "models" / "champion" / "random_forest_champion.pkl"
CHAMPION_METADATA_PATH = PROJECT_ROOT / "models" / "champion" / "champion_metadata.json"
CHALLENGER_MODEL_PATH = (
    PROJECT_ROOT / "models" / "challengers" / "mlp_neural_network_challenger.pkl"
)
CHALLENGER_RESULT_PATH = PROJECT_ROOT / "reports" / "neural_network_experiment.json"
AB_RESULT_PATH = PROJECT_ROOT / "reports" / "offline_ab_test_results.json"
DECISION_PATH = PROJECT_ROOT / "reports" / "conditional_promotion_decision.json"
HISTORY_DIR = PROJECT_ROOT / "models" / "champion" / "history"
CHALLENGER_VERSION = "mlp_neural_network_challenger_v0.1.0"


class PromotionRejected(RuntimeError):
    """Raised when an apply request does not satisfy every promotion gate."""


def evaluate_promotion(
    champion_metadata: dict,
    challenger_result: dict,
    ab_result: dict,
    artifact_evidence: dict,
    *,
    challenger_version: str = CHALLENGER_VERSION,
) -> dict:
    """Return an auditable decision without changing any model artifact."""

    champion_metrics = champion_metadata["champion_validation_metrics"]
    challenger_train = challenger_result["metrics"]["train"]
    challenger_validation = challenger_result["metrics"]["validation"]

    champion_f1 = float(champion_metrics["f1_canceled"])
    challenger_f1 = float(challenger_validation["f1_canceled"])
    f1_improvement = challenger_f1 - champion_f1
    overfitting_gap = abs(
        float(challenger_train["f1_canceled"]) - challenger_f1
    )
    precision_degradation = max(
        0.0,
        float(champion_metrics["precision_canceled"])
        - float(challenger_validation["precision_canceled"]),
    )
    recall_degradation = max(
        0.0,
        float(champion_metrics["recall_canceled"])
        - float(challenger_validation["recall_canceled"]),
    )
    ab_comparison = ab_result["comparison"]
    ab_lower_bound = float(ab_comparison["bootstrap_95_percent_ci"]["lower"])

    gates = {
        "artifact_loadable": bool(artifact_evidence["loadable"]),
        "same_input_contract": bool(artifact_evidence["same_input_contract"]),
        "version_and_artifact_registered": bool(
            challenger_version and artifact_evidence["artifact_exists"]
        ),
        "comparable_validation_evidence": bool(
            challenger_result["split_policy"]["evaluation"] == "validation"
            and not challenger_result["split_policy"]["final_test_used"]
            and ab_result["split_policy"]["source"] == "validation"
            and not ab_result["split_policy"]["final_test_used"]
        ),
        "minimum_f1_improvement": f1_improvement >= MIN_F1_IMPROVEMENT,
        "overfitting_below_limit": overfitting_gap < MAX_OVERFITTING_GAP,
        "critical_metrics_within_limit": bool(
            precision_degradation <= MAX_CRITICAL_METRIC_DEGRADATION
            and recall_degradation <= MAX_CRITICAL_METRIC_DEGRADATION
        ),
        "ab_win_statistically_supported": bool(
            ab_comparison["statistically_supported_challenger_win"]
            and ab_lower_bound > 0
        ),
    }
    eligible = all(gates.values())

    return {
        "policy_version": "conditional_promotion_v1",
        "evaluation_date": date.today().isoformat(),
        "champion_model_version": champion_metadata["model_version"],
        "challenger_model_version": challenger_version,
        "primary_metric": "f1_canceled",
        "thresholds": {
            "minimum_absolute_f1_improvement": MIN_F1_IMPROVEMENT,
            "maximum_train_validation_f1_gap": MAX_OVERFITTING_GAP,
            "maximum_critical_metric_degradation": MAX_CRITICAL_METRIC_DEGRADATION,
            "ab_confidence_interval_lower_bound_must_exceed": 0.0,
        },
        "observed": {
            "champion_validation_f1": champion_f1,
            "challenger_validation_f1": challenger_f1,
            "absolute_f1_improvement": f1_improvement,
            "challenger_train_validation_f1_gap": overfitting_gap,
            "precision_degradation": precision_degradation,
            "recall_degradation": recall_degradation,
            "ab_f1_difference": float(
                ab_comparison["challenger_minus_champion_f1"]
            ),
            "ab_95_percent_ci_lower": ab_lower_bound,
            "ab_95_percent_ci_upper": float(
                ab_comparison["bootstrap_95_percent_ci"]["upper"]
            ),
        },
        "gates": gates,
        "eligible_for_promotion": eligible,
        "decision": "promote_challenger" if eligible else "retain_champion",
        "failed_gates": [name for name, passed in gates.items() if not passed],
        "safety": {
            "data_drift_can_trigger_promotion": False,
            "automatic_apply": False,
            "explicit_apply_flag_required": True,
        },
    }


def inspect_artifacts(champion_path: Path, challenger_path: Path) -> dict:
    """Verify loadability and compare the fitted input feature contract."""

    evidence = {
        "artifact_exists": challenger_path.is_file(),
        "loadable": False,
        "same_input_contract": False,
        "challenger_sha256": None,
    }
    if not champion_path.is_file() or not challenger_path.is_file():
        return evidence

    try:
        champion = _load_pickle(champion_path)
        challenger = _load_pickle(challenger_path)
        champion_features = list(champion.feature_names_in_)
        challenger_features = list(challenger.feature_names_in_)
        evidence.update(
            {
                "loadable": all(
                    hasattr(model, "predict") and hasattr(model, "predict_proba")
                    for model in (champion, challenger)
                ),
                "same_input_contract": champion_features == challenger_features,
                "challenger_sha256": _sha256(challenger_path),
            }
        )
    except (AttributeError, OSError, pickle.UnpicklingError):
        return evidence
    return evidence


def apply_promotion(
    decision: dict,
    *,
    challenger_path: Path,
    champion_path: Path,
    metadata_path: Path,
    history_dir: Path,
    challenger_result: dict,
) -> dict:
    """Atomically replace the Champion after every policy gate has passed."""

    if not decision["eligible_for_promotion"]:
        raise PromotionRejected(
            "Promotion rejected; failed gates: " + ", ".join(decision["failed_gates"])
        )

    history_dir.mkdir(parents=True, exist_ok=True)
    current_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    previous_version = current_metadata["model_version"]
    artifact_backup = history_dir / f"{previous_version}.pkl"
    metadata_backup = history_dir / f"{previous_version}.json"
    shutil.copy2(champion_path, artifact_backup)
    shutil.copy2(metadata_path, metadata_backup)

    temporary_model = champion_path.with_suffix(".pkl.tmp")
    temporary_metadata = metadata_path.with_suffix(".json.tmp")
    shutil.copy2(challenger_path, temporary_model)

    promoted_metadata = deepcopy(current_metadata)
    promoted_metadata.update(
        {
            "model_version": decision["challenger_model_version"],
            "model_type": challenger_result["model_type"],
            "selection_date": decision["evaluation_date"],
            "source_artifact": _relative_path(challenger_path),
            "champion_artifact": _relative_path(champion_path),
            "champion_train_metrics": challenger_result["metrics"]["train"],
            "champion_validation_metrics": challenger_result["metrics"]["validation"],
            "champion_overfitting_gap": decision["observed"][
                "challenger_train_validation_f1_gap"
            ],
            "passes_under_5_percent_rule": True,
            "previous_champion_version": previous_version,
            "conditional_promotion": decision,
            "decision": (
                "Promoted by conditional_promotion_v1 after all metric, "
                "stability, contract and A/B gates passed."
            ),
        }
    )
    temporary_metadata.write_text(
        json.dumps(promoted_metadata, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    try:
        _load_pickle(temporary_model)
        json.loads(temporary_metadata.read_text(encoding="utf-8"))
        os.replace(temporary_model, champion_path)
        os.replace(temporary_metadata, metadata_path)
    except Exception:
        temporary_model.unlink(missing_ok=True)
        temporary_metadata.unlink(missing_ok=True)
        shutil.copy2(artifact_backup, champion_path)
        shutil.copy2(metadata_backup, metadata_path)
        raise

    return promoted_metadata


def run(*, apply: bool = False) -> dict:
    """Evaluate the repository candidate and optionally apply its promotion."""

    champion_metadata = _load_json(CHAMPION_METADATA_PATH)
    challenger_result = _load_json(CHALLENGER_RESULT_PATH)
    ab_result = _load_json(AB_RESULT_PATH)
    evidence = inspect_artifacts(CHAMPION_MODEL_PATH, CHALLENGER_MODEL_PATH)
    decision = evaluate_promotion(
        champion_metadata,
        challenger_result,
        ab_result,
        evidence,
    )
    decision["artifact_evidence"] = evidence
    DECISION_PATH.write_text(
        json.dumps(decision, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    if apply:
        apply_promotion(
            decision,
            challenger_path=CHALLENGER_MODEL_PATH,
            champion_path=CHAMPION_MODEL_PATH,
            metadata_path=CHAMPION_METADATA_PATH,
            history_dir=HISTORY_DIR,
            challenger_result=challenger_result,
        )
    return decision


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_pickle(path: Path):
    with path.open("rb") as file:
        return pickle.load(file)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Replace the Champion only when every promotion gate passes.",
    )
    args = parser.parse_args()
    decision = run(apply=args.apply)
    print(json.dumps(decision, indent=2, ensure_ascii=True))
    print(f"Decision saved to: {DECISION_PATH}")


if __name__ == "__main__":
    main()
