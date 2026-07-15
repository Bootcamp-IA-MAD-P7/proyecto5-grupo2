from functools import lru_cache
import json
import pickle
from pathlib import Path
from uuid import uuid4

import pandas as pd

from app.backend.schemas import ModelInfoResponse, PredictionRequest, PredictionResponse
from src.features.preprocessing import FEATURE_COLUMNS


PROJECT_ROOT = Path(__file__).resolve().parents[3]
METADATA_PATH = PROJECT_ROOT / "models" / "champion" / "champion_metadata.json"
MODEL_STATUS = "loaded"
PRIMARY_METRIC = "f1_score_canceled"
POSITIVE_CLASS = "Canceled"


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
    probability = round(float(model.predict_proba(features)[0][1]), 4)
    risk_level, risk_label = _risk_from_probability(probability)

    return PredictionResponse(
        prediction_id=str(uuid4()),
        prediction="Canceled" if prediction_label == 1 else "Not_Canceled",
        prediction_label=prediction_label,
        probability=probability,
        risk_level=risk_level,
        risk_label=risk_label,
        model_version=load_model_metadata()["model_version"],
        main_factors=_explain_primary_factors(payload),
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
