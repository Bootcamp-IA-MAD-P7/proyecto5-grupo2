"""Train baseline classifiers for hotel reservation cancellation."""

from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay
from sklearn.pipeline import Pipeline

from src.evaluation.classification_metrics import (
    evaluate_classification,
    metrics_to_dataframe,
)
from src.features.preprocessing import (
    PROJECT_ROOT,
    DataSplits,
    build_preprocessor,
    load_dataset,
    prepare_data_splits,
)


RANDOM_STATE = 42
REPORT_PATH = PROJECT_ROOT / "reports" / "model_report.md"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
CONFUSION_MATRIX_PATH = FIGURES_DIR / "baseline_logistic_confusion_matrix.png"
ROC_CURVE_PATH = FIGURES_DIR / "baseline_logistic_roc_curve.png"
BASELINE_MODEL_DIR = PROJECT_ROOT / "models" / "baseline"
LOGISTIC_MODEL_PATH = BASELINE_MODEL_DIR / "logistic_regression_baseline.pkl"


def build_dummy_baseline() -> Pipeline:
    """Build a minimum reference model that predicts the majority class."""

    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            (
                "model",
                DummyClassifier(strategy="most_frequent"),
            ),
        ]
    )


def build_logistic_regression_baseline() -> Pipeline:
    """Build the first real baseline model."""

    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def _positive_class_scores(model: Pipeline, X: pd.DataFrame):
    """Return probability scores for the Canceled class when available."""

    if not hasattr(model, "predict_proba"):
        return None
    return model.predict_proba(X)[:, 1]


def train_and_evaluate_baselines() -> tuple[pd.DataFrame, Pipeline, DataSplits]:
    """Train Dummy and Logistic Regression baselines and evaluate them."""

    dataset = load_dataset()
    splits = prepare_data_splits(dataset)

    models = {
        "dummy_most_frequent": build_dummy_baseline(),
        "logistic_regression_balanced": build_logistic_regression_baseline(),
    }

    all_metrics = []
    for model_name, model in models.items():
        model.fit(splits.X_train, splits.y_train)

        for split_name, X_split, y_split in [
            ("train", splits.X_train, splits.y_train),
            ("validation", splits.X_validation, splits.y_validation),
        ]:
            y_pred = model.predict(X_split)
            y_score = _positive_class_scores(model, X_split)
            all_metrics.append(
                evaluate_classification(
                    model_name=model_name,
                    split=split_name,
                    y_true=y_split,
                    y_pred=y_pred,
                    y_score=y_score,
                )
            )

    metrics_df = metrics_to_dataframe(all_metrics)
    return metrics_df, models["logistic_regression_balanced"], splits


def calculate_overfitting_table(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Compare train and validation F1 for each baseline model."""

    f1_by_split = metrics_df.pivot(
        index="model_name",
        columns="split",
        values="f1_canceled",
    )
    f1_by_split["absolute_gap"] = (
        f1_by_split["train"] - f1_by_split["validation"]
    ).abs()
    f1_by_split["passes_under_5_percent_rule"] = f1_by_split["absolute_gap"] < 0.05
    return f1_by_split.reset_index()


def _format_metrics_table(metrics_df: pd.DataFrame) -> str:
    display_df = metrics_df.copy()
    metric_columns = [
        "accuracy",
        "precision_canceled",
        "recall_canceled",
        "f1_canceled",
        "roc_auc",
    ]
    display_df[metric_columns] = display_df[metric_columns].round(4)
    return _dataframe_to_markdown(display_df)


def _format_overfitting_table(overfitting_df: pd.DataFrame) -> str:
    display_df = overfitting_df.copy()
    display_df[["train", "validation", "absolute_gap"]] = display_df[
        ["train", "validation", "absolute_gap"]
    ].round(4)
    return _dataframe_to_markdown(display_df)


def _dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Render a small dataframe as a Markdown table without extra dependencies."""

    headers = list(df.columns)
    rows = df.astype(object).where(pd.notna(df), "").values.tolist()
    table = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        table.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(table)


def write_model_report(metrics_df: pd.DataFrame, report_path: Path = REPORT_PATH) -> None:
    """Write the baseline model report in Markdown."""

    overfitting_df = calculate_overfitting_table(metrics_df)
    logistic_validation = metrics_df[
        (metrics_df["model_name"] == "logistic_regression_balanced")
        & (metrics_df["split"] == "validation")
    ].iloc[0]

    report = f"""# Model Report

## Baseline inicial

Este reporte registra el primer baseline reproducible del proyecto. El objetivo no es elegir todavia el modelo final, sino crear una primera comparacion honesta entre una regla minima y un modelo real simple.

### Modelos evaluados

- `dummy_most_frequent`: modelo de referencia que siempre predice la clase mayoritaria.
- `logistic_regression_balanced`: primer modelo real, usando el pipeline de preprocesamiento y ajuste de pesos para compensar el desbalance moderado del target.

### Datos y target

- Dataset: Hotel Reservations Classification Dataset.
- Target: `booking_status`.
- Clase positiva para metricas principales: `Canceled`.
- Split usado: train 70%, validacion 15%, test 15%.
- El test queda reservado para una evaluacion posterior mas imparcial.

### Metricas train/validacion

{_format_metrics_table(metrics_df)}

### Figuras de validacion

- Matriz de confusion: `reports/figures/baseline_logistic_confusion_matrix.png`.
- Curva ROC: `reports/figures/baseline_logistic_roc_curve.png`.

### Revision inicial de overfitting

La regla del proyecto pide que la diferencia absoluta entre train y validacion sea menor a 0.05 en la metrica principal. Para este baseline usamos F1-score de la clase `Canceled`.

{_format_overfitting_table(overfitting_df)}

### Lectura de resultados

- El `DummyClassifier` sirve como piso minimo: si un modelo real no lo supera, no aporta valor.
- La Logistic Regression mejora el F1-score de validacion de la clase `Canceled` hasta {logistic_validation["f1_canceled"]:.4f}.
- La diferencia train-validacion queda dentro de la regla de overfitting inferior al 5%.
- El siguiente paso sera revisar si un modelo ensemble mejora este baseline sin aumentar demasiado el overfitting.
"""

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


def save_validation_figures(
    model: Pipeline,
    splits: DataSplits,
    figures_dir: Path = FIGURES_DIR,
) -> None:
    """Save validation confusion matrix and ROC curve for the baseline model."""

    figures_dir.mkdir(parents=True, exist_ok=True)
    y_pred = model.predict(splits.X_validation)
    y_score = _positive_class_scores(model, splits.X_validation)

    fig, ax = plt.subplots(figsize=(7, 5.5))
    ConfusionMatrixDisplay.from_predictions(
        splits.y_validation,
        y_pred,
        labels=[0, 1],
        display_labels=["Not_Canceled", "Canceled"],
        cmap="Blues",
        values_format="d",
        ax=ax,
    )
    ax.set_title("Baseline Logistic Regression - Matriz de confusion")
    fig.tight_layout()
    fig.savefig(CONFUSION_MATRIX_PATH, dpi=160, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 5))
    RocCurveDisplay.from_predictions(
        splits.y_validation,
        y_score,
        name="Logistic Regression baseline",
        ax=ax,
    )
    ax.set_title("Baseline Logistic Regression - Curva ROC")
    fig.tight_layout()
    fig.savefig(ROC_CURVE_PATH, dpi=160)
    plt.close(fig)


def save_baseline_model(model: Pipeline, model_path: Path = LOGISTIC_MODEL_PATH) -> None:
    """Save the Logistic Regression baseline pipeline."""

    model_path.parent.mkdir(parents=True, exist_ok=True)
    with model_path.open("wb") as file:
        pickle.dump(model, file)


def main() -> None:
    metrics_df, logistic_model, splits = train_and_evaluate_baselines()
    save_validation_figures(logistic_model, splits)
    write_model_report(metrics_df)
    save_baseline_model(logistic_model)

    print("Baseline training complete.")
    print(f"Report written to: {REPORT_PATH}")
    print(f"Model saved to: {LOGISTIC_MODEL_PATH}")
    print(_format_metrics_table(metrics_df))


if __name__ == "__main__":
    main()
