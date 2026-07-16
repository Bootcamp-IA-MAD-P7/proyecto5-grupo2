import hashlib
import json
import pickle
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from src.mlops.conditional_promotion import (
    AB_RESULT_PATH,
    CHALLENGER_MODEL_PATH,
    CHALLENGER_RESULT_PATH,
    CHAMPION_METADATA_PATH,
    CHAMPION_MODEL_PATH,
    PromotionRejected,
    apply_promotion,
    evaluate_promotion,
    inspect_artifacts,
)


class ConditionalPromotionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.champion_metadata = json.loads(
            CHAMPION_METADATA_PATH.read_text(encoding="utf-8")
        )
        cls.challenger_result = json.loads(
            CHALLENGER_RESULT_PATH.read_text(encoding="utf-8")
        )
        cls.ab_result = json.loads(AB_RESULT_PATH.read_text(encoding="utf-8"))
        cls.artifact_evidence = inspect_artifacts(
            CHAMPION_MODEL_PATH,
            CHALLENGER_MODEL_PATH,
        )

    def test_current_inferior_challenger_is_rejected(self):
        decision = self._current_decision()

        self.assertEqual(decision["decision"], "retain_champion")
        self.assertFalse(decision["eligible_for_promotion"])
        self.assertIn("minimum_f1_improvement", decision["failed_gates"])
        self.assertIn("ab_win_statistically_supported", decision["failed_gates"])

    def test_candidate_must_pass_every_gate(self):
        challenger = deepcopy(self.challenger_result)
        champion_validation = self.champion_metadata["champion_validation_metrics"]
        challenger["metrics"]["validation"].update(
            {
                "f1_canceled": champion_validation["f1_canceled"] + 0.03,
                "precision_canceled": champion_validation["precision_canceled"],
                "recall_canceled": champion_validation["recall_canceled"],
            }
        )
        challenger["metrics"]["train"]["f1_canceled"] = (
            challenger["metrics"]["validation"]["f1_canceled"] + 0.02
        )
        ab_result = deepcopy(self.ab_result)
        ab_result["comparison"].update(
            {
                "challenger_minus_champion_f1": 0.03,
                "bootstrap_95_percent_ci": {"lower": 0.01, "upper": 0.05},
                "statistically_supported_challenger_win": True,
            }
        )

        decision = evaluate_promotion(
            self.champion_metadata,
            challenger,
            ab_result,
            self.artifact_evidence,
        )

        self.assertTrue(decision["eligible_for_promotion"])
        self.assertEqual(decision["decision"], "promote_challenger")
        self.assertEqual(decision["failed_gates"], [])

    def test_rejected_apply_never_changes_champion(self):
        decision = self._current_decision()
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            champion_path = temp_dir / "champion.pkl"
            challenger_path = temp_dir / "challenger.pkl"
            metadata_path = temp_dir / "champion_metadata.json"
            history_dir = temp_dir / "history"
            champion_path.write_bytes(CHAMPION_MODEL_PATH.read_bytes())
            challenger_path.write_bytes(CHALLENGER_MODEL_PATH.read_bytes())
            metadata_path.write_text(
                json.dumps(self.champion_metadata),
                encoding="utf-8",
            )
            before_hash = self._hash(champion_path)

            with self.assertRaises(PromotionRejected):
                apply_promotion(
                    decision,
                    challenger_path=challenger_path,
                    champion_path=champion_path,
                    metadata_path=metadata_path,
                    history_dir=history_dir,
                    challenger_result=self.challenger_result,
                )

            self.assertEqual(self._hash(champion_path), before_hash)
            self.assertEqual(
                json.loads(metadata_path.read_text(encoding="utf-8"))["model_version"],
                self.champion_metadata["model_version"],
            )
            self.assertFalse(history_dir.exists())

    def test_data_drift_is_never_a_promotion_trigger(self):
        decision = self._current_decision()

        self.assertFalse(decision["safety"]["data_drift_can_trigger_promotion"])
        self.assertFalse(decision["safety"]["automatic_apply"])
        self.assertTrue(decision["safety"]["explicit_apply_flag_required"])

    def test_eligible_apply_replaces_artifact_and_preserves_backup(self):
        decision = self._current_decision()
        decision.update(
            {
                "eligible_for_promotion": True,
                "decision": "promote_challenger",
                "failed_gates": [],
            }
        )
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            champion_path = temp_dir / "champion.pkl"
            challenger_path = temp_dir / "challenger.pkl"
            metadata_path = temp_dir / "champion_metadata.json"
            history_dir = temp_dir / "history"
            champion_path.write_bytes(CHAMPION_MODEL_PATH.read_bytes())
            challenger_path.write_bytes(CHALLENGER_MODEL_PATH.read_bytes())
            metadata_path.write_text(
                json.dumps(self.champion_metadata),
                encoding="utf-8",
            )
            previous_version = self.champion_metadata["model_version"]
            challenger_hash = self._hash(challenger_path)

            promoted_metadata = apply_promotion(
                decision,
                challenger_path=challenger_path,
                champion_path=champion_path,
                metadata_path=metadata_path,
                history_dir=history_dir,
                challenger_result=self.challenger_result,
            )

            self.assertEqual(self._hash(champion_path), challenger_hash)
            self.assertEqual(
                promoted_metadata["model_version"],
                decision["challenger_model_version"],
            )
            self.assertTrue((history_dir / f"{previous_version}.pkl").is_file())
            self.assertTrue((history_dir / f"{previous_version}.json").is_file())
            with champion_path.open("rb") as file:
                promoted_model = pickle.load(file)
            self.assertTrue(hasattr(promoted_model, "predict_proba"))

    def _current_decision(self):
        return evaluate_promotion(
            self.champion_metadata,
            self.challenger_result,
            self.ab_result,
            self.artifact_evidence,
        )

    @staticmethod
    def _hash(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
