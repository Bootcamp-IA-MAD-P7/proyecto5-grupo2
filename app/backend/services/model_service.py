from functools import lru_cache
import json
import pickle
from pathlib import Path
from uuid import uuid4

import pandas as pd

from app.backend.schemas import (
    ModelInfoResponse,
    PredictionRequest,
    PredictionResponse,
    RiskFactorResponse,
)
from src.features.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN, load_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[3]
METADATA_PATH = PROJECT_ROOT / "models" / "champion" / "champion_metadata.json"
MODEL_STATUS = "loaded"
PRIMARY_METRIC = "f1_score_canceled"
POSITIVE_CLASS = "Canceled"
EXPLAINABLE_FEATURES = {
    "lead_time": {
        "label": "Antelación de la reserva",
        "action": "Confirmar la intención de viaje y programar recordatorios anticipados.",
    },
    "no_of_special_requests": {
        "label": "Solicitudes especiales",
        "action": "Contactar al huésped para personalizar la estancia y reforzar su compromiso.",
    },
    "avg_price_per_room": {
        "label": "Precio medio por habitación",
        "action": "Revisar la tarifa, las condiciones y las alternativas de valor ofrecidas.",
    },
    "market_segment_type": {
        "label": "Canal de reserva",
        "action": "Aplicar un seguimiento específico para el canal de procedencia.",
    },
    "no_of_previous_cancellations": {
        "label": "Cancelaciones anteriores",
        "action": "Priorizar el contacto temprano y confirmar las condiciones de la reserva.",
    },
    "no_of_previous_bookings_not_canceled": {
        "label": "Reservas previas completadas",
        "action": "Reforzar beneficios de fidelización y reconocer el historial del huésped.",
    },
    "repeated_guest": {
        "label": "Huésped repetidor",
        "action": "Adaptar el contacto según su relación previa con el hotel.",
    },
    "type_of_meal_plan": {
        "label": "Plan de comidas",
        "action": "Confirmar que el plan elegido sigue ajustándose a las necesidades del huésped.",
    },
    "room_type_reserved": {
        "label": "Tipo de habitación",
        "action": "Validar disponibilidad y ofrecer alternativas equivalentes cuando sea necesario.",
    },
}
INTEGER_REFERENCE_FEATURES = {
    "lead_time",
    "no_of_special_requests",
    "no_of_previous_cancellations",
    "no_of_previous_bookings_not_canceled",
    "repeated_guest",
}


@lru_cache(maxsize=1)
def load_model_metadata() -> dict:
    with METADATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def get_model_path() -> Path:
    metadata = load_model_metadata()
    return PROJECT_ROOT / metadata["champion_artifact"]


@lru_cache(maxsize=1)
def load_model():
    with get_model_path().open("rb") as file:
        return pickle.load(file)


def get_model_info() -> ModelInfoResponse:
    metadata_exists = METADATA_PATH.exists()
    model_path = get_model_path() if metadata_exists else None
    model_loaded = bool(model_path and model_path.exists())
    metadata = load_model_metadata() if metadata_exists else {}
    notes = [
        "Champion Random Forest pipeline loaded from repository artifact.",
        "The pipeline includes preprocessing and binary cancellation classification.",
        "Champion selection metadata is stored in models/champion/champion_metadata.json.",
    ]

    return ModelInfoResponse(
        model_loaded=model_loaded,
        model_version=metadata.get("model_version", "missing_champion_metadata"),
        model_status=MODEL_STATUS if model_loaded else "missing_model_artifact",
        model_type=metadata.get("model_type", "unknown"),
        primary_metric=metadata.get("primary_metric", PRIMARY_METRIC),
        target="booking_status",
        positive_class=metadata.get("positive_class", POSITIVE_CLASS),
        notes=notes,
    )


def predict_cancellation(payload: PredictionRequest) -> PredictionResponse:
    model = load_model()
    features = _payload_to_features(payload)
    prediction_label = int(model.predict(features)[0])
    raw_probability = float(model.predict_proba(features)[0][1])
    probability = round(raw_probability, 4)
    risk_level, risk_label = _risk_from_probability(probability)
    risk_factors = _estimate_risk_factors(model, features, raw_probability)

    return PredictionResponse(
        prediction_id=str(uuid4()),
        prediction="Canceled" if prediction_label == 1 else "Not_Canceled",
        prediction_label=prediction_label,
        probability=probability,
        risk_level=risk_level,
        risk_label=risk_label,
        model_version=load_model_metadata()["model_version"],
        main_factors=[factor.label for factor in risk_factors] or _explain_primary_factors(payload),
        risk_factors=risk_factors,
        recommendation=_recommendation_from_risk(risk_level),
    )


def _payload_to_features(payload: PredictionRequest) -> pd.DataFrame:
    payload_dict = payload.model_dump()
    return pd.DataFrame([payload_dict])[FEATURE_COLUMNS]


def _risk_from_probability(probability: float) -> tuple[str, str]:
    if probability >= 0.7:
        return "high", "Alto"
    if probability >= 0.4:
        return "medium", "Medio"
    return "low", "Bajo"


@lru_cache(maxsize=1)
def _non_canceled_reference_values() -> dict:
    dataset = load_dataset()
    reference_population = dataset[dataset[TARGET_COLUMN] == "Not_Canceled"]
    references = {}

    for feature in EXPLAINABLE_FEATURES:
        values = reference_population[feature].dropna()
        if values.empty:
            continue

        if feature in INTEGER_REFERENCE_FEATURES:
            references[feature] = int(round(float(values.median())))
        elif feature == "avg_price_per_room":
            references[feature] = float(values.median())
        else:
            references[feature] = values.mode().iloc[0]

    return references


def _estimate_risk_factors(
    model,
    features: pd.DataFrame,
    base_probability: float,
    limit: int = 3,
) -> list[RiskFactorResponse]:
    current_values = features.iloc[0].to_dict()
    reference_values = _non_canceled_reference_values()
    counterfactual_rows = []
    compared_features = []

    for feature in EXPLAINABLE_FEATURES:
        if feature not in reference_values:
            continue

        current_value = current_values[feature]
        reference_value = reference_values[feature]
        if current_value == reference_value:
            continue

        counterfactual_row = dict(current_values)
        counterfactual_row[feature] = reference_value
        counterfactual_rows.append(counterfactual_row)
        compared_features.append((feature, current_value, reference_value))

    if not counterfactual_rows:
        return []

    counterfactual_frame = pd.DataFrame(counterfactual_rows)[FEATURE_COLUMNS]
    counterfactual_scores = model.predict_proba(counterfactual_frame)[:, 1]
    factors = []

    for (feature, current_value, reference_value), counterfactual_score in zip(
        compared_features,
        counterfactual_scores,
        strict=True,
    ):
        impact = round(max(0.0, (base_probability - float(counterfactual_score)) * 100), 1)
        if impact < 0.1:
            continue

        factor_config = EXPLAINABLE_FEATURES[feature]
        factors.append(
            RiskFactorResponse(
                feature=feature,
                label=factor_config["label"],
                current_value=_format_factor_value(feature, current_value),
                reference_value=_format_factor_value(feature, reference_value),
                impact_percentage_points=impact,
                action=factor_config["action"],
            )
        )

    return sorted(
        factors,
        key=lambda factor: factor.impact_percentage_points,
        reverse=True,
    )[:limit]


def _format_factor_value(feature: str, value) -> str:
    if feature == "lead_time":
        return f"{int(value)} días"
    if feature == "avg_price_per_room":
        return f"{float(value):.2f} EUR"
    if feature == "repeated_guest":
        return "Sí" if int(value) == 1 else "No"
    return str(value)


def _explain_primary_factors(payload: PredictionRequest) -> list[str]:
    factors = []

    if payload.lead_time >= 90:
        factors.append("Lead time elevado")
    if payload.no_of_special_requests == 0:
        factors.append("Sin solicitudes especiales")
    if payload.market_segment_type in {"Online", "Offline"}:
        factors.append("Segmento con cancelacion frecuente")
    if payload.repeated_guest:
        factors.append("Huesped repetido")
    if payload.no_of_previous_cancellations > 0:
        factors.append("Historial de cancelaciones previas")

    return factors[:3] or ["Patron de reserva evaluado por el modelo"]


def _recommendation_from_risk(risk_level: str) -> str:
    if risk_level == "high":
        return (
            "Activar contacto proactivo, confirmar intencion de viaje y "
            "proteger inventario con lista de espera."
        )

    if risk_level == "medium":
        return (
            "Enviar confirmacion personalizada y ofrecer una mejora o servicio "
            "adicional de bajo coste."
        )

    return (
        "Mantener la reserva en seguimiento ligero y priorizar una experiencia "
        "de llegada impecable."
    )
