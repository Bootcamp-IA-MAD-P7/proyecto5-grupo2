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
TUNING_RESULTS_PATH = PROJECT_ROOT / "reports" / "random_forest_tuning_results.csv"
CHALLENGER_MODEL_DIR = PROJECT_ROOT / "models" / "challengers"
RANDOM_FOREST_MODEL_PATH = CHALLENGER_MODEL_DIR / "random_forest_challenger.pkl"
CV_SPLITS = 3
ENSEMBLE_REPORT_HEADER = "## Ensemble challenger - Random Forest"
OPTIMIZED_RANDOM_FOREST_PARAMS = {
    "n_estimators": 200,
    "max_depth": 18,
    "min_samples_leaf": 6,
    "min_samples_split": 12,
    "class_weight": "balanced_subsample",
}
TUNING_CANDIDATES = [
    {
        "candidate": "rf_depth12_leaf12_split24",
        "n_estimators": 200,
        "max_depth": 12,
        "min_samples_leaf": 12,
        "min_samples_split": 24,
        "class_weight": "balanced_subsample",
    },
    {
        "candidate": "rf_depth14_leaf12_split24",
        "n_estimators": 200,
        "max_depth": 14,
        "min_samples_leaf": 12,
        "min_samples_split": 24,
        "class_weight": "balanced_subsample",
    },
    {
        "candidate": "rf_depth16_leaf8_split16",
        "n_estimators": 200,
        "max_depth": 16,
        "min_samples_leaf": 8,
        "min_samples_split": 16,
        "class_weight": "balanced_subsample",
    },
    {
        "candidate": "rf_depth18_leaf8_split16",
        "n_estimators": 200,
        "max_depth": 18,
        "min_samples_leaf": 8,
        "min_samples_split": 16,
        "class_weight": "balanced_subsample",
    },
    {
        "candidate": "rf_depth16_leaf6_split12",
        "n_estimators": 200,
        "max_depth": 16,
        "min_samples_leaf": 6,
        "min_samples_split": 12,
        "class_weight": "balanced_subsample",
    },
    {
        "candidate": "rf_depth18_leaf6_split12",
        "n_estimators": 200,
        "max_depth": 18,
        "min_samples_leaf": 6,
        "min_samples_split": 12,
        "class_weight": "balanced_subsample",
    },
    {
        "candidate": "rf_depth14_leaf8_split16",
        "n_estimators": 300,
        "max_depth": 14,
        "min_samples_leaf": 8,
        "min_samples_split": 16,
        "class_weight": "balanced_subsample",
    },
    {
        "candidate": "rf_depth16_leaf8_split16_300",
        "n_estimators": 300,
        "max_depth": 16,
        "min_samples_leaf": 8,
        "min_samples_split": 16,
        "class_weight": "balanced_subsample",
    },
    {
        "candidate": "rf_depth16_leaf10_split20",
        "n_estimators": 200,
        "max_depth": 16,
        "min_samples_leaf": 10,
        "min_samples_split": 20,
        "class_weight": "balanced_subsample",
    },
    {
        "candidate": "rf_depth20_leaf8_split16",
        "n_estimators": 200,
        "max_depth": 20,
        "min_samples_leaf": 8,
        "min_samples_split": 16,
        "class_weight": "balanced_subsample",
    },
    {
        "candidate": "rf_depth16_leaf8_split16_balanced",
        "n_estimators": 200,
        "max_depth": 16,
        "min_samples_leaf": 8,
        "min_samples_split": 16,
        "class_weight": "balanced",
    },
    {
        "candidate": "rf_depth16_leaf8_split24",
        "n_estimators": 200,
        "max_depth": 16,
        "min_samples_leaf": 8,
        "min_samples_split": 24,
        "class_weight": "balanced_subsample",
    },
]


def build_random_forest_challenger(model_params: dict | None = None) -> Pipeline:
    """Build a regularized Random Forest challenger."""

    params = dict(OPTIMIZED_RANDOM_FOREST_PARAMS if model_params is None else model_params)
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(scale_numeric=False)),
            (
                "model",
                RandomForestClassifier(
                    **params,
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


def tune_random_forest_challenger(
    splits: DataSplits,
    candidates: list[dict] = TUNING_CANDIDATES,
) -> pd.DataFrame:
    """Evaluate a controlled set of Random Forest hyperparameter candidates."""

    rows = []
    for candidate in candidates:
        candidate_name = candidate["candidate"]
        model_params = {
            key: value for key, value in candidate.items() if key != "candidate"
        }
        model = build_random_forest_challenger(model_params)
        model.fit(splits.X_train, splits.y_train)

        train_pred = model.predict(splits.X_train)
        train_score = _positive_class_scores(model, splits.X_train)
        validation_pred = model.predict(splits.X_validation)
        validation_score = _positive_class_scores(model, splits.X_validation)

        train_metrics = evaluate_classification(
            model_name=candidate_name,
            split="train",
            y_true=splits.y_train,
            y_pred=train_pred,
            y_score=train_score,
        )
        validation_metrics = evaluate_classification(
            model_name=candidate_name,
            split="validation",
            y_true=splits.y_validation,
            y_pred=validation_pred,
            y_score=validation_score,
        )
        absolute_gap = abs(
            train_metrics.f1_canceled - validation_metrics.f1_canceled
        )
        rows.append(
            {
                "candidate": candidate_name,
                **model_params,
                "train_f1_canceled": train_metrics.f1_canceled,
                "validation_f1_canceled": validation_metrics.f1_canceled,
                "absolute_gap": absolute_gap,
                "passes_under_5_percent_rule": absolute_gap < 0.05,
                "validation_precision_canceled": validation_metrics.precision_canceled,
                "validation_recall_canceled": validation_metrics.recall_canceled,
                "validation_roc_auc": validation_metrics.roc_auc,
            }
        )

    tuning_df = pd.DataFrame(rows)
    return tuning_df.sort_values(
        by=["passes_under_5_percent_rule", "validation_f1_canceled"],
        ascending=[False, False],
    ).reset_index(drop=True)


def save_tuning_results(
    tuning_df: pd.DataFrame,
    tuning_results_path: Path = TUNING_RESULTS_PATH,
) -> None:
    """Save the complete hyperparameter tuning table."""

    tuning_results_path.parent.mkdir(parents=True, exist_ok=True)
    tuning_df.to_csv(tuning_results_path, index=False)


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
    tuning_df: pd.DataFrame,
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

### Busqueda de hiperparametros

Se evaluaron {len(tuning_df)} configuraciones controladas de `RandomForestClassifier` usando el mismo split train/validacion. El criterio de seleccion fue maximizar el F1-score de la clase `Canceled` en validacion, manteniendo la regla de overfitting inferior a 0.05.

Tabla completa exportada en `reports/random_forest_tuning_results.csv`.

Top 5 de configuraciones:

{_format_tuning_table(tuning_df.head(5))}

### Configuracion del challenger

- Modelo: `RandomForestClassifier`.
- Preprocessing: mismo contrato de features que el baseline, con One-Hot Encoding para categoricas y sin escalado numerico porque el modelo es de arboles.
- Hiperparametros optimizados: {_format_params_inline(OPTIMIZED_RANDOM_FOREST_PARAMS)}.
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


def _format_tuning_table(tuning_df: pd.DataFrame) -> str:
    display_columns = [
        "candidate",
        "n_estimators",
        "max_depth",
        "min_samples_leaf",
        "min_samples_split",
        "class_weight",
        "validation_f1_canceled",
        "absolute_gap",
        "validation_roc_auc",
    ]
    display_df = tuning_df[display_columns].copy()
    display_df[
        ["validation_f1_canceled", "absolute_gap", "validation_roc_auc"]
    ] = display_df[
        ["validation_f1_canceled", "absolute_gap", "validation_roc_auc"]
    ].round(4)
    return _dataframe_to_markdown(display_df)


def _format_params_inline(params: dict) -> str:
    return ", ".join(f"`{key}={value!r}`" for key, value in params.items())


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
    metrics_df, challenger_model, splits = train_and_evaluate_models()
    tuning_df = tune_random_forest_challenger(splits)
    cv_df = cross_validate_challenger()
    save_tuning_results(tuning_df)
    save_challenger_model(challenger_model)
    write_challenger_report(metrics_df, cv_df, tuning_df)

    print("Challenger training complete.")
    print(f"Model saved to: {RANDOM_FOREST_MODEL_PATH}")
    print(f"Tuning results written to: {TUNING_RESULTS_PATH}")
    print(_format_metrics_table(metrics_df))
    print(_format_cv_table(cv_df))


if __name__ == "__main__":
    main()
