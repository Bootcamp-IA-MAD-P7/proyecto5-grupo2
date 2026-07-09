import unittest

from src.models.train_baseline import (
    calculate_overfitting_table,
    train_and_evaluate_baselines,
)


class BaselineTrainingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics_df, _, _ = train_and_evaluate_baselines()

    def test_logistic_regression_beats_dummy_on_validation_f1(self):
        validation_metrics = self.metrics_df[self.metrics_df["split"] == "validation"]

        dummy_f1 = validation_metrics.loc[
            validation_metrics["model_name"] == "dummy_most_frequent",
            "f1_canceled",
        ].iloc[0]
        logistic_f1 = validation_metrics.loc[
            validation_metrics["model_name"] == "logistic_regression_balanced",
            "f1_canceled",
        ].iloc[0]

        self.assertGreater(logistic_f1, dummy_f1)
        self.assertGreater(logistic_f1, 0.50)

    def test_logistic_regression_passes_overfitting_rule(self):
        overfitting_df = calculate_overfitting_table(self.metrics_df)
        logistic_row = overfitting_df[
            overfitting_df["model_name"] == "logistic_regression_balanced"
        ].iloc[0]

        self.assertLess(logistic_row["absolute_gap"], 0.05)
        self.assertTrue(logistic_row["passes_under_5_percent_rule"])


if __name__ == "__main__":
    unittest.main()
