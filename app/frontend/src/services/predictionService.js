const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function requestJson(path, options) {
  const response = await fetch(`${API_URL}${path}`, options);

  if (!response.ok) {
    let detail = "";
    try {
      const body = await response.json();
      detail = Array.isArray(body.detail)
        ? body.detail.map((item) => item.msg).join(". ")
        : body.detail || "";
    } catch {
      detail = "";
    }

    throw new Error(detail || `El backend respondió con el estado ${response.status}.`);
  }

  return response.json();
}

export function predictReservation(payload) {
  return requestJson("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export function submitPredictionFeedback(payload) {
  return requestJson("/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export function fetchFeedbackSummary() {
  return requestJson("/feedback/summary");
}

export function fetchModelInfo() {
  return requestJson("/model/info");
}

export function fetchDemoReservations(limit = 16) {
  return requestJson(`/reservations/demo?limit=${limit}`);
}

function toDateString(inputData) {
  const month = String(inputData.arrival_month).padStart(2, "0");
  const day = String(inputData.arrival_date).padStart(2, "0");
  return `${inputData.arrival_year}-${month}-${day}`;
}

export function applyPredictionToReservation(reservation, inputData, prediction) {
  const nights = Number(inputData.no_of_weekend_nights) + Number(inputData.no_of_week_nights);

  return {
    ...reservation,
    arrival: toDateString(inputData),
    nights,
    estimatedStayValue: Math.round(Number(inputData.avg_price_per_room) * Math.max(nights, 1)),
    riskLevel: prediction.risk_level,
    riskPercent: Math.round(Number(prediction.probability) * 100),
    inputData,
    prediction,
    mainFactors: prediction.main_factors,
    recommendation: prediction.recommendation
  };
}

function toFrontendReservation(reservation, prediction) {
  const inputData = reservation.input_data;
  const baseReservation = {
    id: reservation.id,
    guest: reservation.display_name,
    secondaryLabel: `${inputData.market_segment_type} · ${reservation.stay_label}`,
    status: reservation.status_label
  };

  return applyPredictionToReservation(baseReservation, inputData, prediction);
}

export async function fetchPredictedReservations(limit = 16) {
  const response = await fetchDemoReservations(limit);
  const reservations = await Promise.all(
    response.reservations.map(async (reservation) => {
      const prediction = await predictReservation(reservation.input_data);
      return toFrontendReservation(reservation, prediction);
    })
  );

  return {
    reservations,
    returned: response.returned,
    totalAvailable: response.total_available,
    source: response.source
  };
}
