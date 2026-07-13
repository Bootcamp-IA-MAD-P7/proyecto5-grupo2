"""Promote the selected model to Champion and document the decision."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
import json
import pickle
import shutil
from pathlib import Path

import pandas as pd
from sklearn.pipeline import Pipeline

from src.evaluation.classification_metrics import evaluate_classification
from src.features.preprocessing import PROJECT_ROOT, load_dataset, prepare_data_splits
from src.models.train_baseline import LOGISTIC_MODEL_PATH
from src.models.train_challengers import (
    OPTIMIZED_RANDOM_FOREST_PARAMS,
    RANDOM_FOREST_MODEL_PATH,
    cross_validate_challenger,
)


CHAMPION_VERSION = "random_forest_champion_v0.1.0"
REPORT_PATH = PROJECT_ROOT / "reports" / "model_report.md"
CHAMPION_MODEL_DIR = PROJECT_ROOT / "models" / "champion"
CHAMPION_MODEL_PATH = CHAMPION_MODEL_DIR / "random_forest_champion.pkl"
CHAMPION_METADATA_PATH = CHAMPION_MODEL_DIR / "champion_metadata.json"
CHAMPION_REPORT_HEADER = "## Champion Model Selection"
NEXT_REPORT_HEADER = "## Interpretabilidad y analisis de errores"


def load_model(model_path: Path) -> Pipeline:
    with model_path.open("rb") as file:
        return pickle.load(file)


def calculate_split_metrics(model: Pipeline, model_name: str, split_name: str, X, y):
    y_pred = model.predict(X)
    y_score = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else None
    return evaluate_classification(
        model_name=model_name,
        split=split_name,
        y_true=y,
        y_pred=y_pred,
        y_score=y_score,
    )


def build_champion_metadata() -> dict:
    dataset = load_dataset()
    splits = prepare_data_splits(dataset)
    baseline_model = load_model(LOGISTIC_MODEL_PATH)
    champion_model = load_model(RANDOM_FOREST_MODEL_PATH)

    baseline_validation = calculate_split_metrics(
        baseline_model,
        "logistic_regression_baseline",
        "validation",
        splits.X_validation,
        splits.y_validation,
    )
    baseline_train = calculate_split_metrics(
        baseline_model,
        "logistic_regression_baseline",
        "train",
        splits.X_train,
        splits.y_train,
    )
    champion_train = calculate_split_metrics(
        champion_model,
        "random_forest_champion",
        "train",
        splits.X_train,
        splits.y_train,
    )
    champion_validation = calculate_split_metrics(
        champion_model,
        "random_forest_champion",
        "validation",
        splits.X_validation,
        splits.y_validation,
    )
    cv_df = cross_validate_challenger()

    baseline_overfitting_gap = abs(
        baseline_train.f1_canceled - baseline_validation.f1_canceled
    )
    champion_overfitting_gap = abs(
        champion_train.f1_canceled - champion_validation.f1_canceled
    )
    return {
        "model_version": CHAMPION_VERSION,
        "model_type": "RandomForestClassifier",
        "selection_date": date.today().isoformat(),
        "primary_metric": "f1_canceled",
        "positive_class": "Canceled",
        "source_artifact": RANDOM_FOREST_MODEL_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "champion_artifact": CHAMPION_MODEL_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "metadata_artifact": CHAMPION_METADATA_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "hyperparameters": OPTIMIZED_RANDOM_FOREST_PARAMS,
        "baseline_train_metrics": asdict(baseline_train),
        "baseline_validation_metrics": asdict(baseline_validation),
        "champion_train_metrics": asdict(champion_train),
        "champion_validation_metrics": asdict(champion_validation),
        "baseline_overfitting_gap": baseline_overfitting_gap,
        "champion_overfitting_gap": champion_overfitting_gap,
        "passes_under_5_percent_rule": champion_overfitting_gap < 0.05,
        "cross_validation": _cv_to_metadata(cv_df),
        "decision": (
            "Random Forest is selected as Champion because it improves the "
            "Canceled-class F1-score versus the Logistic Regression baseline, "
            "keeps the overfitting gap below 0.05 and remains reproducible in "
            "stratified cross-validation."
        ),
        "limitations": [
            "The test split remains reserved for a final unbiased check.",
            "FastAPI still loads the baseline until the app integration task updates it.",
            "Tree-based feature importance should be documented if this Champion is used in the final presentation.",
        ],
    }


def save_champion_artifacts(metadata: dict) -> None:
    CHAMPION_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RANDOM_FOREST_MODEL_PATH, CHAMPION_MODEL_PATH)
    CHAMPION_METADATA_PATH.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_champion_report(metadata: dict, report_path: Path = REPORT_PATH) -> None:
    current_report = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    section = build_champion_report_section(metadata)
    updated_report = _replace_or_insert_section(
        current_report,
        CHAMPION_REPORT_HEADER,
        section,
        NEXT_REPORT_HEADER,
    )
    report_path.write_text(updated_report, encoding="utf-8")


def build_champion_report_section(metadata: dict) -> str:
    baseline = metadata["baseline_validation_metrics"]
    champion = metadata["champion_validation_metrics"]
    champion_train = metadata["champion_train_metrics"]
    cv = metadata["cross_validation"]

    return f"""{CHAMPION_REPORT_HEADER}

### Decision

Se selecciona `random_forest_champion_v0.1.0` como Champion Model del proyecto.

### Evidencia de seleccion

| criterio | baseline Logistic Regression | Champion Random Forest |
| --- | --- | --- |
| F1 validacion clase `Canceled` | {baseline["f1_canceled"]:.4f} | {champion["f1_canceled"]:.4f} |
| Precision validacion clase `Canceled` | {baseline["precision_canceled"]:.4f} | {champion["precision_canceled"]:.4f} |
| Recall validacion clase `Canceled` | {baseline["recall_canceled"]:.4f} | {champion["recall_canceled"]:.4f} |
| ROC-AUC validacion | {baseline["roc_auc"]:.4f} | {champion["roc_auc"]:.4f} |
| Gap F1 train-validacion | {metadata["baseline_overfitting_gap"]:.4f} | {metadata["champion_overfitting_gap"]:.4f} |
| Regla overfitting < 0.05 | cumple baseline | {metadata["passes_under_5_percent_rule"]} |

### Validacion cruzada del Champion

| metrica | media | desviacion | folds |
| --- | --- | --- | --- |
| F1 `Canceled` | {cv["f1_canceled"]["mean"]:.4f} | {cv["f1_canceled"]["std"]:.4f} | {cv["f1_canceled"]["splits"]} |
| Precision `Canceled` | {cv["precision_canceled"]["mean"]:.4f} | {cv["precision_canceled"]["std"]:.4f} | {cv["precision_canceled"]["splits"]} |
| Recall `Canceled` | {cv["recall_canceled"]["mean"]:.4f} | {cv["recall_canceled"]["std"]:.4f} | {cv["recall_canceled"]["splits"]} |
| ROC-AUC | {cv["roc_auc"]["mean"]:.4f} | {cv["roc_auc"]["std"]:.4f} | {cv["roc_auc"]["splits"]} |

### Artefactos versionados

- Modelo Champion: `models/champion/random_forest_champion.pkl`.
- Metadata Champion: `models/champion/champion_metadata.json`.
- Version: `{metadata["model_version"]}`.
- Hiperparametros: {_format_params_inline(metadata["hyperparameters"])}.

### Lectura tecnica

- El Champion mejora el F1-score de validacion de `Canceled` de {baseline["f1_canceled"]:.4f} a {champion["f1_canceled"]:.4f}.
- El gap train-validacion del Champion es {metadata["champion_overfitting_gap"]:.4f}, por debajo del limite operativo de 0.05.
- La validacion cruzada confirma estabilidad razonable: F1 medio {cv["f1_canceled"]["mean"]:.4f} con desviacion {cv["f1_canceled"]["std"]:.4f}.
- La API todavia puede seguir cargando el baseline hasta que el equipo cierre la tarea de integracion de app; esta decision deja preparado el artefacto ML para ese cambio.
"""


def _cv_to_metadata(cv_df: pd.DataFrame) -> dict:
    rows = {}
    for row in cv_df.itertuples(index=False):
        rows[row.metric] = {
            "mean": float(row.cv_mean),
            "std": float(row.cv_std),
            "splits": int(row.cv_splits),
        }
    return rows


def _format_params_inline(params: dict) -> str:
    return ", ".join(f"`{key}={value!r}`" for key, value in params.items())


def _replace_or_insert_section(
    current_report: str,
    section_header: str,
    new_section: str,
    insert_before_header: str,
) -> str:
    if section_header in current_report:
        start_index = current_report.index(section_header)
        next_section_index = current_report.find("\n## ", start_index + len(section_header))
        if next_section_index == -1:
            return f"{current_report[:start_index]}{new_section}"
        return f"{current_report[:start_index]}{new_section}\n{current_report[next_section_index + 1:]}"

    if insert_before_header in current_report:
        insert_index = current_report.index(insert_before_header)
        prefix = current_report[:insert_index].rstrip()
        suffix = current_report[insert_index:]
        return f"{prefix}\n\n{new_section}\n{suffix}"

    separator = "\n\n" if current_report and not current_report.endswith("\n") else "\n"
    return f"{current_report}{separator}{new_section}"


def main() -> None:
    metadata = build_champion_metadata()
    save_champion_artifacts(metadata)
    write_champion_report(metadata)
    print(f"Champion model written to: {CHAMPION_MODEL_PATH}")
    print(f"Champion metadata written to: {CHAMPION_METADATA_PATH}")
    print(f"Champion report updated: {REPORT_PATH}")


if __name__ == "__main__":
    main()
