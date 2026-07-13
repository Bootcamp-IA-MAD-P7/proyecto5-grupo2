import unittest

from src.models.train_baseline import calculate_overfitting_table
from src.models.train_challengers import (
    build_random_forest_challenger,
    train_and_evaluate_models,
)


class ChallengerTrainingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics_df, _, _ = train_and_evaluate_models()

    def test_random_forest_uses_tuned_hyperparameters(self):
        model = build_random_forest_challenger().named_steps["model"]

        self.assertEqual(model.n_estimators, 200)
        self.assertEqual(model.max_depth, 16)
        self.assertEqual(model.min_samples_leaf, 8)
        self.assertEqual(model.min_samples_split, 16)
        self.assertEqual(model.class_weight, "balanced_subsample")

    def test_random_forest_validation_f1_meets_expected_threshold(self):
        validation_metrics = self.metrics_df[self.metrics_df["split"] == "validation"]
        forest_f1 = validation_metrics.loc[
            validation_metrics["model_name"] == "random_forest_challenger",
            "f1_canceled",
        ].iloc[0]

        self.assertGreaterEqual(forest_f1, 0.80)

    def test_random_forest_passes_overfitting_rule(self):
        overfitting_df = calculate_overfitting_table(self.metrics_df)
        forest_row = overfitting_df[
            overfitting_df["model_name"] == "random_forest_challenger"
        ].iloc[0]

        self.assertLess(forest_row["absolute_gap"], 0.05)
        self.assertTrue(forest_row["passes_under_5_percent_rule"])


if __name__ == "__main__":
    unittest.main()
