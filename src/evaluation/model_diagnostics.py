"""Generate Champion model interpretation and error-analysis sections."""

from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay
from sklearn.pipeline import Pipeline

from src.features.preprocessing import (
    PROJECT_ROOT,
    DataSplits,
    load_dataset,
    prepare_data_splits,
)


MODEL_PATH = PROJECT_ROOT / "models" / "champion" / "random_forest_champion.pkl"
REPORT_PATH = PROJECT_ROOT / "reports" / "model_report.md"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
CONFUSION_MATRIX_PATH = FIGURES_DIR / "champion_random_forest_confusion_matrix.png"
ROC_CURVE_PATH = FIGURES_DIR / "champion_random_forest_roc_curve.png"
FEATURE_IMPORTANCE_PATH = FIGURES_DIR / "champion_random_forest_feature_importance.png"
SECTION_HEADER = "## Interpretabilidad y analisis de errores"


def load_champion_model(model_path: Path = MODEL_PATH) -> Pipeline:
    with model_path.open("rb") as file:
        return pickle.load(file)


def tree_feature_importance(model: Pipeline, top_n: int = 12) -> pd.DataFrame:
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["model"]

    importance = pd.DataFrame(
        {
            "feature": preprocessor.get_feature_names_out(),
            "importance": classifier.feature_importances_,
        }
    )
    importance["share_percent"] = importance["importance"] * 100
    return importance.sort_values("importance", ascending=False).head(top_n)


def validation_error_summary(
    model: Pipeline,
    splits: DataSplits,
) -> dict[str, int | float]:
    y_pred = model.predict(splits.X_validation)
    y_true = splits.y_validation

    false_positive = int(((y_true == 0) & (y_pred == 1)).sum())
    false_negative = int(((y_true == 1) & (y_pred == 0)).sum())
    true_positive = int(((y_true == 1) & (y_pred == 1)).sum())
    true_negative = int(((y_true == 0) & (y_pred == 0)).sum())

    total_canceled = int((y_true == 1).sum())
    total_not_canceled = int((y_true == 0).sum())

    return {
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive_rate": false_positive / total_not_canceled,
        "false_negative_rate": false_negative / total_canceled,
    }


def save_validation_figures(
    model: Pipeline,
    splits: DataSplits,
    importance: pd.DataFrame,
    figures_dir: Path = FIGURES_DIR,
) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    y_pred = model.predict(splits.X_validation)
    y_score = model.predict_proba(splits.X_validation)[:, 1]

    fig, ax = plt.subplots(figsize=(7, 5.5))
    ConfusionMatrixDisplay.from_predictions(
        splits.y_validation,
        y_pred,
        labels=[0, 1],
        display_labels=["Not_Canceled", "Canceled"],
        cmap="Greens",
        values_format="d",
        ax=ax,
    )
    ax.set_title("Champion Random Forest - Matriz de confusion")
    fig.tight_layout()
    fig.savefig(CONFUSION_MATRIX_PATH, dpi=160, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 5))
    RocCurveDisplay.from_predictions(
        splits.y_validation,
        y_score,
        name="Random Forest Champion",
        ax=ax,
    )
    ax.set_title("Champion Random Forest - Curva ROC")
    fig.tight_layout()
    fig.savefig(ROC_CURVE_PATH, dpi=160)
    plt.close(fig)

    plot_df = importance.sort_values("importance", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(plot_df["feature"], plot_df["importance"], color="#2E7D32")
    ax.set_title("Champion Random Forest - Feature importance")
    ax.set_xlabel("Importancia relativa")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(FEATURE_IMPORTANCE_PATH, dpi=160, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display_df = df.copy()
    display_df["importance"] = display_df["importance"].round(4)
    display_df["share_percent"] = display_df["share_percent"].round(2)

    headers = list(display_df.columns)
    rows = display_df.astype(object).where(pd.notna(display_df), "").values.tolist()
    table = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        table.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(table)


def build_diagnostics_section() -> str:
    model = load_champion_model()
    splits = prepare_data_splits(load_dataset())
    importance = tree_feature_importance(model)
    errors = validation_error_summary(model, splits)
    save_validation_figures(model, splits, importance)

    return f"""{SECTION_HEADER}

### Modelo analizado

Esta seccion analiza el Champion productivizado en la API:

- Modelo: `RandomForestClassifier`.
- Artefacto: `models/champion/random_forest_champion.pkl`.
- Version: `random_forest_champion_v0.1.0`.
- Clase positiva: `Canceled`.
- Split analizado: validacion.

### Figuras de validacion

- Matriz de confusion: `reports/figures/champion_random_forest_confusion_matrix.png`.
- Curva ROC: `reports/figures/champion_random_forest_roc_curve.png`.
- Feature importance: `reports/figures/champion_random_forest_feature_importance.png`.

### Feature importance

Para Random Forest se usa `feature_importances_`, que reparte importancia entre las variables usadas por los arboles. Es una lectura global del modelo: indica que variables ayudan mas a separar cancelaciones de no cancelaciones, pero no prueba causalidad.

{dataframe_to_markdown(importance)}

Lectura:

- `lead_time` mantiene una de las senales mas fuertes: reservas hechas con mucha antelacion suelen tener mayor riesgo de cancelacion.
- `no_of_special_requests` aporta mucha senal: cuando hay pocas o ninguna solicitud especial, el riesgo historico de cancelacion tiende a subir.
- `market_segment_type` y variables de historial de reserva tambien ayudan a diferenciar patrones de cancelacion.

### Analisis de errores

| tipo_error | cantidad | lectura |
| --- | --- | --- |
| false_positive | {errors["false_positive"]} | Reservas que el modelo marca como riesgo de cancelacion, pero finalmente no se cancelan. |
| false_negative | {errors["false_negative"]} | Reservas que el modelo no marca como riesgo, pero finalmente se cancelan. |

Tasas sobre validacion:

- False positive rate sobre `Not_Canceled`: {errors["false_positive_rate"]:.4f}.
- False negative rate sobre `Canceled`: {errors["false_negative_rate"]:.4f}.

Interpretacion de negocio:

- Los falsos positivos pueden generar acciones comerciales innecesarias, pero suelen ser menos costosos que perder una cancelacion real no anticipada.
- Los falsos negativos son mas sensibles para negocio porque representan cancelaciones que no se detectaron a tiempo.
- El Champion reduce errores frente al baseline y mantiene el gap de overfitting bajo el limite operativo de 0.05.

### Limitaciones y siguientes mejoras

- El test split sigue reservado para una comprobacion final imparcial antes de defender el resultado como definitivo.
- La importancia de variables es global; para explicar casos individuales convendria anadir explicabilidad local en una fase posterior.
- Como siguiente mejora, el equipo puede ajustar el umbral de decision si quiere priorizar mas recall de `Canceled` o mas precision de las alertas.
"""


def replace_or_append_section(report: str, section: str) -> str:
    if SECTION_HEADER not in report:
        separator = "\n\n" if report and not report.endswith("\n") else "\n"
        return f"{report}{separator}{section}"

    start_index = report.index(SECTION_HEADER)
    next_section_index = report.find("\n## ", start_index + len(SECTION_HEADER))
    if next_section_index == -1:
        return f"{report[:start_index]}{section}"
    return f"{report[:start_index]}{section}\n{report[next_section_index + 1:]}"


def write_diagnostics_report(report_path: Path = REPORT_PATH) -> None:
    current_report = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    section = build_diagnostics_section()
    report_path.write_text(replace_or_append_section(current_report, section), encoding="utf-8")


def main() -> None:
    write_diagnostics_report()
    print(f"Model diagnostics written to: {REPORT_PATH}")
    print(f"Champion figures written to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
