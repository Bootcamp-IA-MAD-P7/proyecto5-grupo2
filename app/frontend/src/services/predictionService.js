const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === "true";

const riskCopy = {
  low: {
    label: "Bajo",
    tone: "low",
    recommendation:
      "Mantener la reserva en seguimiento ligero y priorizar una experiencia de llegada impecable.",
    factors: ["Lead time moderado", "Historial estable", "Solicitud especial registrada"]
  },
  medium: {
    label: "Medio",
    tone: "medium",
    recommendation:
      "Enviar confirmación personalizada y ofrecer una mejora o servicio adicional de bajo coste.",
    factors: ["Canal online", "Precio sensible", "Pocas señales de compromiso"]
  },
  high: {
    label: "Alto",
    tone: "high",
    recommendation:
      "Activar contacto proactivo, confirmar intención de viaje y proteger inventario con lista de espera.",
    factors: ["Lead time elevado", "Sin solicitudes especiales", "Segmento con cancelación frecuente"]
  }
};

function calculateMockProbability(payload) {
  let score = 0.18;
  score += Math.min(Number(payload.lead_time || 0) / 365, 1) * 0.34;
  score += payload.market_segment_type === "Online" ? 0.16 : 0.04;
  score += Number(payload.no_of_special_requests || 0) === 0 ? 0.14 : -0.08;
  score += Number(payload.repeated_guest || 0) ? -0.13 : 0.04;
  score += Number(payload.no_of_previous_cancellations || 0) * 0.09;
  score += Number(payload.avg_price_per_room || 0) > 180 ? 0.06 : 0;
  return Math.max(0.04, Math.min(0.96, score));
}

function riskFromProbability(probability) {
  if (probability >= 0.7) return "high";
  if (probability >= 0.4) return "medium";
  return "low";
}

export async function predictReservation(payload) {
  if (!USE_MOCK_API) {
    const response = await fetch(`${API_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error("No se pudo obtener la predicción del backend.");
    }

    return response.json();
  }

  await new Promise((resolve) => setTimeout(resolve, 520));
  const probability = calculateMockProbability(payload);
  const risk = riskFromProbability(probability);
  const copy = riskCopy[risk];

  return {
    prediction: probability >= 0.5 ? "Canceled" : "Not_Canceled",
    prediction_label: probability >= 0.5 ? 1 : 0,
    probability,
    risk_level: risk,
    risk_label: copy.label,
    model_version: "mock_editorial_v1",
    main_factors: copy.factors,
    recommendation: copy.recommendation
  };
}
