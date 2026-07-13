"""Generate model interpretation and error-analysis sections."""

from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd

from src.features.preprocessing import PROJECT_ROOT, load_dataset, prepare_data_splits


MODEL_PATH = PROJECT_ROOT / "models" / "baseline" / "logistic_regression_baseline.pkl"
REPORT_PATH = PROJECT_ROOT / "reports" / "model_report.md"
SECTION_HEADER = "## Interpretabilidad y analisis de errores"


def load_baseline_model(model_path: Path = MODEL_PATH):
    with model_path.open("rb") as file:
        return pickle.load(file)


def coefficient_importance(model, top_n: int = 12) -> pd.DataFrame:
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["model"]

    importance = pd.DataFrame(
        {
            "feature": preprocessor.get_feature_names_out(),
            "coefficient": classifier.coef_[0],
        }
    )
    importance["absolute_coefficient"] = importance["coefficient"].abs()
    importance["effect_on_canceled"] = importance["coefficient"].apply(
        lambda value: "increases_risk" if value > 0 else "decreases_risk"
    )
    return importance.sort_values("absolute_coefficient", ascending=False).head(top_n)


def validation_error_summary(model) -> dict[str, int | float]:
    dataset = load_dataset()
    splits = prepare_data_splits(dataset)
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


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display_df = df.copy()
    for column in ["coefficient", "absolute_coefficient"]:
        display_df[column] = display_df[column].round(4)

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
    model = load_baseline_model()
    importance = coefficient_importance(model)
    errors = validation_error_summary(model)

    return f"""{SECTION_HEADER}

### Modelo analizado

Esta seccion analiza el baseline productivizado en la API:

- Modelo: `logistic_regression_balanced`.
- Artefacto: `models/baseline/logistic_regression_baseline.pkl`.
- Clase positiva: `Canceled`.
- Split analizado: validacion.

### Feature importance equivalente

Para Logistic Regression se usa el valor absoluto de los coeficientes como aproximacion de importancia. Los coeficientes positivos empujan la prediccion hacia `Canceled`; los negativos empujan hacia `Not_Canceled`.

{dataframe_to_markdown(importance)}

Lectura:

- `lead_time` aparece como una de las senales mas fuertes: reservas con mayor antelacion tienden a elevar el riesgo de cancelacion.
- `no_of_special_requests` tiene coeficiente negativo: mas solicitudes especiales tienden a reducir el riesgo estimado.
- Algunas categorias de `market_segment_type` y `room_type_reserved` aportan senal relevante, pero deben interpretarse como asociaciones historicas, no como causas directas.

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
- Como siguiente mejora, el equipo puede ajustar el umbral de decision si quiere priorizar mas recall de `Canceled` o mas precision de las alertas.

### Limitaciones y siguientes mejoras

- El baseline es funcional y cumple el Nivel Esencial, pero no es necesariamente el mejor modelo final.
- Random Forest ya muestra mejor F1 de validacion como challenger, por lo que puede evaluarse como Champion en el Nivel Medio.
- La interpretabilidad de coeficientes aplica al baseline lineal; si se promueve un modelo de arboles, conviene reportar importancias del modelo final.
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


if __name__ == "__main__":
    main()
