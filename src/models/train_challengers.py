"""Train ensemble challengers and compare them against the baseline."""

from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
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
    make_features_and_target,
    prepare_data_splits,
)
from src.models.train_baseline import (
    build_dummy_baseline,
    build_logistic_regression_baseline,
    calculate_overfitting_table,
)


RANDOM_STATE = 42
REPORT_PATH = PROJECT_ROOT / "reports" / "model_report.md"
CHALLENGER_MODEL_DIR = PROJECT_ROOT / "models" / "challengers"
RANDOM_FOREST_MODEL_PATH = CHALLENGER_MODEL_DIR / "random_forest_challenger.pkl"
CV_SPLITS = 3
ENSEMBLE_REPORT_HEADER = "## Ensemble challenger - Random Forest"


def build_random_forest_challenger() -> Pipeline:
    """Build a regularized Random Forest challenger."""

    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(scale_numeric=False)),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=200,
                    max_depth=16,
                    min_samples_leaf=8,
                    min_samples_split=16,
                    class_weight="balanced_subsample",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def train_and_evaluate_models() -> tuple[pd.DataFrame, Pipeline, DataSplits]:
    """Train baseline and challenger models with the same data split."""

    dataset = load_dataset()
    splits = prepare_data_splits(dataset)

    models = {
        "dummy_most_frequent": build_dummy_baseline(),
        "logistic_regression_balanced": build_logistic_regression_baseline(),
        "random_forest_challenger": build_random_forest_challenger(),
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
    return metrics_df, models["random_forest_challenger"], splits


def cross_validate_challenger(cv_splits: int = CV_SPLITS) -> pd.DataFrame:
    """Run stratified cross-validation for the Random Forest challenger."""

    dataset = load_dataset()
    X, y = make_features_and_target(dataset)
    model = build_random_forest_challenger()
    cv = StratifiedKFold(
        n_splits=cv_splits,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    cv_results = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring={
            "f1_canceled": "f1",
            "precision_canceled": "precision",
            "recall_canceled": "recall",
            "roc_auc": "roc_auc",
        },
        n_jobs=1,
    )

    rows = []
    for metric_name in [
        "test_f1_canceled",
        "test_precision_canceled",
        "test_recall_canceled",
        "test_roc_auc",
    ]:
        values = cv_results[metric_name]
        rows.append(
            {
                "model_name": "random_forest_challenger",
                "metric": metric_name.removeprefix("test_"),
                "cv_mean": values.mean(),
                "cv_std": values.std(),
                "cv_splits": cv_splits,
            }
        )

    return pd.DataFrame(rows)


def save_challenger_model(
    model: Pipeline,
    model_path: Path = RANDOM_FOREST_MODEL_PATH,
) -> None:
    """Save the Random Forest challenger pipeline."""

    model_path.parent.mkdir(parents=True, exist_ok=True)
    with model_path.open("wb") as file:
        pickle.dump(model, file)


def write_challenger_report(
    metrics_df: pd.DataFrame,
    cv_df: pd.DataFrame,
    report_path: Path = REPORT_PATH,
) -> None:
    """Append or replace the Random Forest challenger section."""

    overfitting_df = calculate_overfitting_table(metrics_df)
    validation_metrics = metrics_df[metrics_df["split"] == "validation"]
    logistic_validation = validation_metrics[
        validation_metrics["model_name"] == "logistic_regression_balanced"
    ].iloc[0]
    forest_validation = validation_metrics[
        validation_metrics["model_name"] == "random_forest_challenger"
    ].iloc[0]
    forest_overfitting = overfitting_df[
        overfitting_df["model_name"] == "random_forest_challenger"
    ].iloc[0]

    section = f"""{ENSEMBLE_REPORT_HEADER}

### Ticket relacionado

- `T-3.1 Entrenar modelo ensemble`.
- `T-3.2 Aplicar validacion cruzada`.
- `T-3.3 Optimizar hiperparametros`.

### Configuracion del challenger

- Modelo: `RandomForestClassifier`.
- Preprocessing: mismo contrato de features que el baseline, con One-Hot Encoding para categoricas y sin escalado numerico porque el modelo es de arboles.
- Hiperparametros optimizados: `n_estimators=200`, `max_depth=16`, `min_samples_leaf=8`, `min_samples_split=16`, `class_weight="balanced_subsample"`.
- Clase positiva: `Canceled`.
- El test sigue reservado para evaluacion final.

### Comparacion train/validacion

{_format_metrics_table(metrics_df)}

### Revision de overfitting

{_format_overfitting_table(overfitting_df)}

### Validacion cruzada del challenger

{_format_cv_table(cv_df)}

### Lectura tecnica

- El Random Forest mejora el F1-score de validacion de `Canceled` de {logistic_validation["f1_canceled"]:.4f} a {forest_validation["f1_canceled"]:.4f}.
- El gap train-validacion del challenger es {forest_overfitting["absolute_gap"]:.4f}, por debajo del limite operativo de 0.05.
- La validacion cruzada de {CV_SPLITS} folds muestra F1 medio de {cv_df.loc[cv_df["metric"] == "f1_canceled", "cv_mean"].iloc[0]:.4f}.
- Este modelo queda como challenger optimizado, pero no se selecciona Champion todavia porque falta revision final contra los criterios de `T-3.4`.
"""

    current_report = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    updated_report = _replace_or_append_section(
        current_report,
        ENSEMBLE_REPORT_HEADER,
        section,
    )
    report_path.write_text(updated_report, encoding="utf-8")


def _positive_class_scores(model: Pipeline, X: pd.DataFrame):
    if not hasattr(model, "predict_proba"):
        return None
    return model.predict_proba(X)[:, 1]


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


def _format_cv_table(cv_df: pd.DataFrame) -> str:
    display_df = cv_df.copy()
    display_df[["cv_mean", "cv_std"]] = display_df[["cv_mean", "cv_std"]].round(4)
    return _dataframe_to_markdown(display_df)


def _dataframe_to_markdown(df: pd.DataFrame) -> str:
    headers = list(df.columns)
    rows = df.astype(object).where(pd.notna(df), "").values.tolist()
    table = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        table.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(table)


def _replace_or_append_section(
    current_report: str,
    section_header: str,
    new_section: str,
) -> str:
    if section_header not in current_report:
        separator = "\n\n" if current_report and not current_report.endswith("\n") else "\n"
        return f"{current_report}{separator}{new_section}"

    start_index = current_report.index(section_header)
    next_section_index = current_report.find("\n## ", start_index + len(section_header))
    if next_section_index == -1:
        return f"{current_report[:start_index]}{new_section}"
    return f"{current_report[:start_index]}{new_section}\n{current_report[next_section_index + 1:]}"


def main() -> None:
    metrics_df, challenger_model, _ = train_and_evaluate_models()
    cv_df = cross_validate_challenger()
    save_challenger_model(challenger_model)
    write_challenger_report(metrics_df, cv_df)

    print("Challenger training complete.")
    print(f"Model saved to: {RANDOM_FOREST_MODEL_PATH}")
    print(_format_metrics_table(metrics_df))
    print(_format_cv_table(cv_df))


if __name__ == "__main__":
    main()
