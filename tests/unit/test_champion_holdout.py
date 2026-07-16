import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.evaluation.evaluate_champion_holdout import (
    evaluate_acceptance,
    record_holdout_evaluation,
)


class ChampionHoldoutTest(unittest.TestCase):
    def test_acceptance_requires_minimum_f1_and_stable_gap(self):
        passing = evaluate_acceptance({"f1_canceled": 0.81}, validation_f1=0.82)
        failing = evaluate_acceptance({"f1_canceled": 0.76}, validation_f1=0.82)

        self.assertTrue(passing["passes_all_criteria"])
        self.assertFalse(failing["passes_all_criteria"])

    def test_holdout_result_can_only_be_recorded_once(self):
        with TemporaryDirectory() as directory:
            temp_dir = Path(directory)
            metadata_path = temp_dir / "champion_metadata.json"
            result_path = temp_dir / "champion_test_metrics.json"
            metadata_path.write_text(
                json.dumps(
                    {
                        "model_version": "test_champion",
                        "limitations": [
                            "The test split remains reserved for a final unbiased check."
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = {
                "evaluation_date": "2026-07-15",
                "metrics": {"f1_canceled": 0.81},
                "model_sha256": "model-digest",
                "dataset_sha256": "dataset-digest",
                "split_strategy": {"test_fraction": 0.15},
                "acceptance": {"passes_all_criteria": True},
                "policy": "No tuning after the final holdout.",
            }

            record_holdout_evaluation(
                result,
                metadata_path=metadata_path,
                result_path=result_path,
            )

            saved_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(saved_metadata["champion_test_metrics"]["f1_canceled"], 0.81)
            self.assertTrue(result_path.exists())

            with self.assertRaisesRegex(RuntimeError, "already been recorded"):
                record_holdout_evaluation(
                    result,
                    metadata_path=metadata_path,
                    result_path=result_path,
                )


if __name__ == "__main__":
    unittest.main()
