const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function predictReservation(payload) {
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

export async function submitPredictionFeedback(payload) {
  const response = await fetch(`${API_URL}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("No se pudo guardar el feedback de la predicción.");
  }

  return response.json();
}

export async function fetchFeedbackSummary() {
  const response = await fetch(`${API_URL}/feedback/summary`);

  if (!response.ok) {
    throw new Error("No se pudo obtener el resumen de feedback.");
  }

  return response.json();
}

export async function fetchModelInfo() {
  const response = await fetch(`${API_URL}/model/info`);

  if (!response.ok) {
    throw new Error("No se pudo obtener la información del modelo.");
  }

  return response.json();
}

export async function fetchDemoReservations(limit = 8) {
  const response = await fetch(`${API_URL}/reservations/demo?limit=${limit}`);

  if (!response.ok) {
    throw new Error("No se pudieron obtener reservas del backend.");
  }

  return response.json();
}

function toDateString(inputData) {
  const month = String(inputData.arrival_month).padStart(2, "0");
  const day = String(inputData.arrival_date).padStart(2, "0");
  return `${inputData.arrival_year}-${month}-${day}`;
}

function daysUntilArrival(dateString) {
  const arrival = new Date(dateString);
  const today = new Date();
  const diffTime = arrival - today;
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

function toFrontendReservation(reservation, prediction) {
  const inputData = reservation.input_data;
  const nights = Number(inputData.no_of_weekend_nights) + Number(inputData.no_of_week_nights);
  const arrival = toDateString(inputData);

  return {
    id: reservation.id,
    guest: reservation.display_name,
    email: `${inputData.market_segment_type} · ${reservation.stay_label}`,
    arrival,
    nights,
    price: Math.round(Number(inputData.avg_price_per_room) * Math.max(nights, 1)),
    riskLevel: prediction.risk_level,
    riskPercent: Math.round(Number(prediction.probability) * 100),
    daysLeft: daysUntilArrival(arrival),
    status: reservation.status_label,
    inputData,
    prediction,
    mainFactors: prediction.main_factors,
    recommendation: prediction.recommendation
  };
}

export async function fetchPredictedReservations(limit = 8) {
  const response = await fetchDemoReservations(limit);
  const reservations = await Promise.all(
    response.reservations.map(async (reservation) => {
      const prediction = await predictReservation(reservation.input_data);
      return toFrontendReservation(reservation, prediction);
    })
  );

  return reservations;
}
