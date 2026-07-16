"""Expose versioned expert-level experiment evidence to monitoring clients."""

import json
from functools import lru_cache
from pathlib import Path

from app.backend.schemas import (
    ABExperimentResponse,
    MonitoringExperimentsResponse,
    NeuralExperimentResponse,
    PromotionExperimentResponse,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
NEURAL_RESULT_PATH = PROJECT_ROOT / "reports" / "neural_network_experiment.json"
AB_RESULT_PATH = PROJECT_ROOT / "reports" / "offline_ab_test_results.json"
PROMOTION_RESULT_PATH = PROJECT_ROOT / "reports" / "conditional_promotion_decision.json"


@lru_cache(maxsize=1)
def get_experiment_overview() -> MonitoringExperimentsResponse:
    """Build a stable API contract from repository experiment artifacts."""

    neural = _load_json(NEURAL_RESULT_PATH)
    ab_result = _load_json(AB_RESULT_PATH)
    promotion = _load_json(PROMOTION_RESULT_PATH)

    neural_comparison = neural["comparison"]
    ab_arms = ab_result["arms"]
    ab_comparison = ab_result["comparison"]

    return MonitoringExperimentsResponse(
        evidence_source="versioned_repository_artifacts",
        neural_network=NeuralExperimentResponse(
            status="completed",
            model_type=neural["model_type"],
            train_f1=neural["metrics"]["train"]["f1_canceled"],
            validation_f1=neural["metrics"]["validation"]["f1_canceled"],
            overfitting_gap=neural_comparison["train_validation_f1_gap"],
            decision=neural["decision"],
        ),
        ab_testing=ABExperimentResponse(
            status="completed",
            experiment_id=ab_result["experiment_id"],
            champion_rows=ab_arms["A"]["rows"],
            challenger_rows=ab_arms["B"]["rows"],
            champion_f1=ab_arms["A"]["metrics"]["f1_canceled"],
            challenger_f1=ab_arms["B"]["metrics"]["f1_canceled"],
            ci_lower=ab_comparison["bootstrap_95_percent_ci"]["lower"],
            ci_upper=ab_comparison["bootstrap_95_percent_ci"]["upper"],
            decision=ab_result["decision"],
        ),
        conditional_promotion=PromotionExperimentResponse(
            status="completed",
            policy_version=promotion["policy_version"],
            eligible=promotion["eligible_for_promotion"],
            failed_gates=promotion["failed_gates"],
            decision=promotion["decision"],
        ),
    )


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
