from app.backend.schemas import ModelInfoResponse, PredictionRequest, PredictionResponse


MODEL_VERSION = "mock_api_v0"
MODEL_STATUS = "waiting_for_champion_model"
PRIMARY_METRIC = "f1_score_canceled"
MODEL_TYPE = "mock"
MODEL_LOADED = False


def get_model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        model_loaded=MODEL_LOADED,
        model_version=MODEL_VERSION,
        model_status=MODEL_STATUS,
        model_type=MODEL_TYPE,
        primary_metric=PRIMARY_METRIC,
        target="booking_status",
        positive_class="Canceled",
        notes=[
            "Provisional mock model used until ML Core delivers the Champion Model.",
            "The real model must preserve the current prediction response contract.",
        ],
    )


def predict_cancellation(payload: PredictionRequest) -> PredictionResponse:
    probability = _mock_probability(payload)
    risk_level, risk_label = _risk_from_probability(probability)
    factors, recommendation = _mock_explanation(risk_level)

    return PredictionResponse(
        prediction="Canceled" if probability >= 0.5 else "Not_Canceled",
        prediction_label=1 if probability >= 0.5 else 0,
        probability=probability,
        risk_level=risk_level,
        risk_label=risk_label,
        model_version=MODEL_VERSION,
        main_factors=factors,
        recommendation=recommendation,
    )


def _mock_probability(payload: PredictionRequest) -> float:
    score = 0.18
    score += min(payload.lead_time / 365, 1) * 0.34
    score += 0.16 if payload.market_segment_type == "Online" else 0.04
    score += 0.14 if payload.no_of_special_requests == 0 else -0.08
    score += -0.13 if payload.repeated_guest else 0.04
    score += payload.no_of_previous_cancellations * 0.09
    score += 0.06 if payload.avg_price_per_room > 180 else 0
    return round(max(0.04, min(0.96, score)), 4)


def _risk_from_probability(probability: float) -> tuple[str, str]:
    if probability >= 0.7:
        return "high", "Alto"
    if probability >= 0.4:
        return "medium", "Medio"
    return "low", "Bajo"


def _mock_explanation(risk_level: str) -> tuple[list[str], str]:
    if risk_level == "high":
        return (
            [
                "Lead time elevado",
                "Sin solicitudes especiales",
                "Segmento con cancelacion frecuente",
            ],
            (
                "Activar contacto proactivo, confirmar intencion de viaje y "
                "proteger inventario con lista de espera."
            ),
        )

    if risk_level == "medium":
        return (
            ["Canal online", "Precio sensible", "Pocas senales de compromiso"],
            (
                "Enviar confirmacion personalizada y ofrecer una mejora o servicio "
                "adicional de bajo coste."
            ),
        )

    return (
        ["Lead time moderado", "Historial estable", "Solicitud especial registrada"],
        (
            "Mantener la reserva en seguimiento ligero y priorizar una experiencia "
            "de llegada impecable."
        ),
    )
