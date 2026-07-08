from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import HealthResponse, PredictionRequest, PredictionResponse


app = FastAPI(
    title="Hotel Insights API",
    version="0.1.0",
    description="Initial prediction API for hotel reservation cancellation risk.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    probability = _mock_probability(payload)
    risk_level, risk_label = _risk_from_probability(probability)

    if risk_level == "high":
        factors = [
            "Lead time elevado",
            "Sin solicitudes especiales",
            "Segmento con cancelacion frecuente",
        ]
        recommendation = (
            "Activar contacto proactivo, confirmar intencion de viaje y "
            "proteger inventario con lista de espera."
        )
    elif risk_level == "medium":
        factors = ["Canal online", "Precio sensible", "Pocas senales de compromiso"]
        recommendation = (
            "Enviar confirmacion personalizada y ofrecer una mejora o servicio "
            "adicional de bajo coste."
        )
    else:
        factors = ["Lead time moderado", "Historial estable", "Solicitud especial registrada"]
        recommendation = (
            "Mantener la reserva en seguimiento ligero y priorizar una experiencia "
            "de llegada impecable."
        )

    return PredictionResponse(
        prediction="Canceled" if probability >= 0.5 else "Not_Canceled",
        prediction_label=1 if probability >= 0.5 else 0,
        probability=probability,
        risk_level=risk_level,
        risk_label=risk_label,
        model_version="mock_api_v0",
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
