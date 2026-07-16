import unittest

import numpy as np

from src.features.preprocessing import load_dataset, prepare_data_splits
from src.mlops.offline_ab_test import assign_ab_arms, run_offline_ab_test


class OfflineABTestingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.splits = prepare_data_splits(load_dataset())
        cls.result, cls.assignments = run_offline_ab_test()

    def test_assignment_is_deterministic_disjoint_and_complete(self):
        champion_first, challenger_first = assign_ab_arms(self.splits.y_validation)
        champion_second, challenger_second = assign_ab_arms(self.splits.y_validation)

        np.testing.assert_array_equal(champion_first, champion_second)
        np.testing.assert_array_equal(challenger_first, challenger_second)
        self.assertEqual(len(np.intersect1d(champion_first, challenger_first)), 0)
        self.assertEqual(
            len(champion_first) + len(challenger_first),
            len(self.splits.y_validation),
        )

    def test_experiment_uses_80_20_stratified_validation_cohorts(self):
        policy = self.result["split_policy"]
        self.assertEqual(policy["source"], "validation")
        self.assertFalse(policy["final_test_used"])
        self.assertAlmostEqual(policy["champion_share"], 0.80)
        self.assertAlmostEqual(policy["challenger_share"], 0.20)
        self.assertLess(
            self.result["cohort_balance"]["absolute_positive_rate_difference"],
            0.002,
        )

    def test_each_row_has_one_unique_auditable_prediction(self):
        self.assertEqual(len(self.assignments), len(self.splits.y_validation))
        self.assertEqual(self.assignments["prediction_id"].nunique(), len(self.assignments))
        self.assertEqual(set(self.assignments["arm"]), {"A", "B"})
        self.assertFalse(self.assignments["source_row_index"].duplicated().any())

    def test_decision_retains_champion_when_challenger_has_no_supported_win(self):
        comparison = self.result["comparison"]
        self.assertFalse(comparison["statistically_supported_challenger_win"])
        self.assertEqual(self.result["decision"], "retain_champion")


if __name__ == "__main__":
    unittest.main()
