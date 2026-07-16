import unittest

import numpy as np

from src.features.preprocessing import (
    TARGET_COLUMN,
    build_preprocessor,
    load_dataset,
    make_features_and_target,
    prepare_data_splits,
)


class PreprocessingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_dataset()

    def test_features_exclude_identifier_and_target(self):
        X, y = make_features_and_target(self.df)

        self.assertNotIn("Booking_ID", X.columns)
        self.assertNotIn(TARGET_COLUMN, X.columns)
        self.assertEqual(len(X), len(y))
        self.assertEqual(set(y.unique()), {0, 1})

    def test_missing_required_column_is_rejected(self):
        invalid_df = self.df.drop(columns=["lead_time"])

        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            make_features_and_target(invalid_df)

    def test_unknown_target_class_is_rejected(self):
        invalid_df = self.df.copy()
        invalid_df.loc[invalid_df.index[0], TARGET_COLUMN] = "Unknown_Status"

        with self.assertRaisesRegex(ValueError, "Unknown target classes"):
            make_features_and_target(invalid_df)

    def test_stratified_splits_keep_target_distribution(self):
        splits = prepare_data_splits(self.df)
        full_rate = self.df[TARGET_COLUMN].eq("Canceled").mean()

        self.assertAlmostEqual(splits.y_train.mean(), full_rate, places=3)
        self.assertAlmostEqual(splits.y_validation.mean(), full_rate, places=3)
        self.assertAlmostEqual(splits.y_test.mean(), full_rate, places=3)

    def test_preprocessor_transforms_train_and_validation(self):
        splits = prepare_data_splits(self.df)
        preprocessor = build_preprocessor()

        X_train_ready = preprocessor.fit_transform(splits.X_train)
        X_validation_ready = preprocessor.transform(splits.X_validation)

        self.assertEqual(X_train_ready.shape[0], len(splits.X_train))
        self.assertEqual(X_validation_ready.shape[0], len(splits.X_validation))
        self.assertEqual(X_train_ready.shape[1], X_validation_ready.shape[1])
        self.assertFalse(np.isnan(X_train_ready).any())
        self.assertFalse(np.isnan(X_validation_ready).any())


if __name__ == "__main__":
    unittest.main()
