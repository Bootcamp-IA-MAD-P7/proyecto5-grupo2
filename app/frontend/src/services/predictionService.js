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

export function predictReservation(payload, source = "frontend_manual") {
  return requestJson("/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Prediction-Source": source
    },
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

export function fetchFeedbackHistory() {
  return requestJson("/feedback");
}

export function updateFeedbackRecord(recordId, payload) {
  return requestJson(`/feedback/${recordId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export function fetchModelInfo() {
  return requestJson("/model/info");
}

export function fetchDemoReservations(limit = 16, offset = 0) {
  const query = new URLSearchParams({
    limit: String(limit),
    offset: String(offset)
  });
  return requestJson(`/reservations/demo?${query.toString()}`);
}

export function fetchDemoReservationById(bookingId) {
  return requestJson(`/reservations/demo/${encodeURIComponent(bookingId)}`);
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
    riskFactors: prediction.risk_factors || [],
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

export async function fetchPredictedReservations(limit = 16, offset = 0) {
  const response = await fetchDemoReservations(limit, offset);
  const reservations = await Promise.all(
    response.reservations.map(async (reservation) => {
      const prediction = await predictReservation(reservation.input_data, "frontend_demo_queue");
      return toFrontendReservation(reservation, prediction);
    })
  );

  return {
    reservations,
    returned: response.returned,
    totalAvailable: response.total_available,
    limit: response.limit ?? limit,
    offset: response.offset ?? offset,
    hasMore: response.has_more ?? offset + response.returned < response.total_available,
    source: response.source
  };
}

export async function fetchPredictedReservationById(bookingId) {
  const reservation = await fetchDemoReservationById(bookingId);
  const prediction = await predictReservation(
    reservation.input_data,
    "frontend_demo_queue"
  );
  return toFrontendReservation(reservation, prediction);
}
