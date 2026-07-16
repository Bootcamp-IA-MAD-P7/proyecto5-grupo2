import unittest

from sklearn.neural_network import MLPClassifier

from src.models.train_neural_network import (
    MODEL_NAME,
    NEURAL_NETWORK_PARAMS,
    build_experiment_result,
    build_neural_network_challenger,
    train_and_evaluate_neural_network,
)


class NeuralNetworkExperimentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics_df, cls.model, _ = train_and_evaluate_neural_network()
        cls.result = build_experiment_result(cls.metrics_df, cls.model)

    def test_builder_uses_shared_preprocessing_and_controlled_mlp(self):
        pipeline = build_neural_network_challenger()
        self.assertEqual(list(pipeline.named_steps), ["preprocessor", "model"])
        self.assertIsInstance(pipeline.named_steps["model"], MLPClassifier)

        for parameter_name, expected_value in NEURAL_NETWORK_PARAMS.items():
            self.assertEqual(
                getattr(pipeline.named_steps["model"], parameter_name),
                expected_value,
            )

    def test_experiment_reports_train_and_validation_without_final_test(self):
        self.assertEqual(set(self.metrics_df["split"]), {"train", "validation"})
        self.assertEqual(set(self.metrics_df["model_name"]), {MODEL_NAME})
        self.assertFalse(self.result["split_policy"]["final_test_used"])

    def test_decision_matches_metrics_and_overfitting_policy(self):
        comparison = self.result["comparison"]
        expected_decision = (
            "eligible_for_controlled_comparison"
            if comparison["improves_champion_f1"]
            and comparison["passes_under_5_percent_overfitting_rule"]
            else "retain_champion"
        )
        self.assertEqual(self.result["decision"], expected_decision)
        self.assertGreaterEqual(
            self.result["metrics"]["validation"]["f1_canceled"],
            0.65,
        )


if __name__ == "__main__":
    unittest.main()
