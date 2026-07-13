import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  BedDouble,
  CalendarDays,
  CheckCircle2,
  Hotel,
  MessageSquare,
  RefreshCw,
  ShieldCheck,
  TrendingUp
} from "lucide-react";
import {
  fetchFeedbackSummary,
  fetchModelInfo,
  predictReservation,
  submitPredictionFeedback
} from "./services/predictionService";
import "./betaStyles.css";

const reservations = [
  {
    id: "RSV-1027",
    guest: "Laura Gomez",
    stay: "Suite urbana",
    arrivalMonth: 7,
    arrivalDate: 15,
    status: "Pendiente de confirmar",
    values: {
      lead_time: 120,
      arrival_year: 2018,
      arrival_month: 7,
      arrival_date: 15,
      no_of_special_requests: 0,
      avg_price_per_room: 156,
      market_segment_type: "Online",
      no_of_weekend_nights: 1,
      no_of_week_nights: 2,
      type_of_meal_plan: "Meal Plan 1",
      room_type_reserved: "Room_Type 1",
      no_of_adults: 2,
      no_of_children: 0,
      required_car_parking_space: 0,
      repeated_guest: 0,
      no_of_previous_cancellations: 0,
      no_of_previous_bookings_not_canceled: 0
    }
  },
  {
    id: "RSV-1184",
    guest: "Marco Silva",
    stay: "Retiro familiar",
    arrivalMonth: 8,
    arrivalDate: 22,
    status: "Alta anticipacion",
    values: {
      lead_time: 168,
      arrival_year: 2018,
      arrival_month: 8,
      arrival_date: 22,
      no_of_special_requests: 0,
      avg_price_per_room: 186,
      market_segment_type: "Online",
      no_of_weekend_nights: 1,
      no_of_week_nights: 4,
      type_of_meal_plan: "Meal Plan 1",
      room_type_reserved: "Room_Type 4",
      no_of_adults: 2,
      no_of_children: 1,
      required_car_parking_space: 0,
      repeated_guest: 0,
      no_of_previous_cancellations: 1,
      no_of_previous_bookings_not_canceled: 0
    }
  },
  {
    id: "RSV-1210",
    guest: "Ana Torres",
    stay: "Cliente repetidor",
    arrivalMonth: 9,
    arrivalDate: 6,
    status: "Baja friccion",
    values: {
      lead_time: 28,
      arrival_year: 2018,
      arrival_month: 9,
      arrival_date: 6,
      no_of_special_requests: 2,
      avg_price_per_room: 148,
      market_segment_type: "Offline",
      no_of_weekend_nights: 2,
      no_of_week_nights: 3,
      type_of_meal_plan: "Meal Plan 1",
      room_type_reserved: "Room_Type 2",
      no_of_adults: 2,
      no_of_children: 0,
      required_car_parking_space: 1,
      repeated_guest: 1,
      no_of_previous_cancellations: 0,
      no_of_previous_bookings_not_canceled: 3
    }
  }
];

const monthNames = {
  1: "enero",
  2: "febrero",
  3: "marzo",
  4: "abril",
  5: "mayo",
  6: "junio",
  7: "julio",
  8: "agosto",
  9: "septiembre",
  10: "octubre",
  11: "noviembre",
  12: "diciembre"
};

const channelLabels = {
  Online: "Canal online",
  Offline: "Canal directo/offline",
  Corporate: "Empresa",
  Complementary: "Cortesía",
  Aviation: "Aerolínea"
};

const fieldGroups = [
  {
    title: "Señales de reserva",
    helper: "Datos que suelen anticipar cambios antes de la llegada.",
    fields: [
      ["lead_time", "Antelación", "number", null, "días"],
      ["market_segment_type", "Canal", "select", ["Online", "Offline", "Corporate", "Complementary", "Aviation"]],
      ["avg_price_per_room", "Precio medio", "number", null, "€"],
      ["no_of_special_requests", "Solicitudes", "number"]
    ]
  },
  {
    title: "Estancia",
    helper: "Contexto de llegada y duración de la reserva.",
    fields: [
      ["arrival_month", "Mes", "number"],
      ["arrival_date", "Día", "number"],
      ["no_of_weekend_nights", "Noches fin de semana", "number"],
      ["no_of_week_nights", "Noches entre semana", "number"]
    ]
  },
  {
    title: "Huésped",
    helper: "Señales de compromiso y relación previa.",
    fields: [
      ["no_of_adults", "Adultos", "number"],
      ["no_of_children", "Niños", "number"],
      ["repeated_guest", "Repetidor", "select", [0, 1]],
      ["required_car_parking_space", "Parking", "select", [0, 1]]
    ]
  }
];

function riskTitle(result) {
  if (!result) return "Sin calcular";
  if (result.risk_level === "high") return "Revisión prioritaria";
  if (result.risk_level === "medium") return "Seguimiento recomendado";
  return "Llegada estable";
}

function formatArrival(reservation) {
  return `${reservation.arrivalDate} de ${monthNames[reservation.arrivalMonth]}`;
}

function formatCurrency(value) {
  return new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0
  }).format(Number(value));
}

function riskDescription(result) {
  if (!result) return "Selecciona una reserva y calcula el riesgo para activar una recomendación operativa.";
  if (result.risk_level === "high") {
    return "Conviene contactar antes del cierre, confirmar intención de viaje y proteger inventario.";
  }
  if (result.risk_level === "medium") {
    return "La reserva merece seguimiento ligero y una confirmación personalizada.";
  }
  return "La reserva no muestra señales urgentes. Mantener observación normal.";
}

export default function BetaApp() {
  const [selectedId, setSelectedId] = useState(reservations[0].id);
  const selectedReservation = reservations.find((item) => item.id === selectedId) ?? reservations[0];
  const [form, setForm] = useState(selectedReservation.values);
  const [result, setResult] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [feedbackSummary, setFeedbackSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [feedbackState, setFeedbackState] = useState("idle");

  useEffect(() => {
    fetchModelInfo().then(setModelInfo).catch(() => setModelInfo(null));
    fetchFeedbackSummary().then(setFeedbackSummary).catch(() => setFeedbackSummary(null));
  }, []);

  function selectReservation(reservation) {
    setSelectedId(reservation.id);
    setForm(reservation.values);
    setResult(null);
    setFeedbackState("idle");
  }

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function calculateRisk() {
    setIsLoading(true);
    setFeedbackState("idle");
    try {
      const prediction = await predictReservation(form);
      setResult(prediction);
    } finally {
      setIsLoading(false);
    }
  }

  async function sendFeedback(userFeedback, actualStatus = null) {
    if (!result) return;
    setFeedbackState("saving");
    await submitPredictionFeedback({
      input_data: form,
      prediction: result.prediction,
      probability: result.probability,
      risk_level: result.risk_level,
      model_version: result.model_version,
      user_feedback: userFeedback,
      actual_status: actualStatus,
      comments: `Feedback desde beta para ${selectedReservation.id}`,
      source: "frontend_beta"
    });
    const summary = await fetchFeedbackSummary();
    setFeedbackSummary(summary);
    setFeedbackState("saved");
  }

  const probability = result ? Math.round(result.probability * 100) : null;
  const nights = useMemo(
    () => Number(form.no_of_weekend_nights) + Number(form.no_of_week_nights),
    [form.no_of_weekend_nights, form.no_of_week_nights]
  );
  const roomRevenue = Number(form.avg_price_per_room) * nights;
  const leadSignal = Math.min(Math.round((Number(form.lead_time) / 180) * 100), 100);
  const requestSignal = Math.max(10, 100 - Number(form.no_of_special_requests) * 30);
  const priceSignal = Math.min(Math.round((Number(form.avg_price_per_room) / 220) * 100), 100);

  return (
    <main className="beta-shell">
      <header className="beta-header">
        <div className="beta-brand">
          <img className="beta-logo" src="/logo.png" alt="Hotel Insights" />
          <div>
            <strong>Hotel Insights</strong>
            <small>Guest risk studio</small>
          </div>
        </div>
        <div className="beta-status">
          <span>
            <ShieldCheck size={16} />
            {modelInfo?.model_loaded ? "Motor predictivo activo" : "Modelo no disponible"}
          </span>
          <span>
            <MessageSquare size={16} />
            Aprendizajes registrados: {feedbackSummary?.total_records ?? 0}
          </span>
        </div>
      </header>

      <section className="beta-hero">
        <div className="hero-media" aria-hidden="true">
          <img src="/hotel-bg.jpg" alt="" />
        </div>
        <div className="hero-copy">
          <span className="beta-eyebrow">Reservas inteligentes</span>
          <h1>Decide antes de que una reserva se enfríe.</h1>
          <p>
            Hotel Insights convierte señales de estancia, canal y huésped en una prioridad clara
            para equipos que necesitan proteger ocupación e ingresos sin añadir ruido operativo.
          </p>
          <a href="#review" className="hero-action">
            Revisar llegadas
            <ArrowRight size={18} />
          </a>
        </div>
      </section>

      <section className="story-strip" aria-label="Resumen de operacion">
        <article>
          <span>Reservas a revisar</span>
          <strong>{reservations.length}</strong>
          <small>Llegadas con señales pendientes</small>
        </article>
        <article>
          <span>Ingreso en observación</span>
          <strong>{formatCurrency(roomRevenue)}</strong>
          <small>Estancia seleccionada</small>
        </article>
        <article>
          <span>Aprendizaje acumulado</span>
          <strong>{feedbackSummary?.total_records ?? 0}</strong>
          <small>Registros de feedback</small>
        </article>
      </section>

      <section id="review" className="vertical-section">
        <div className="section-heading">
          <span className="beta-eyebrow">Llegadas próximas</span>
          <h2>Empieza por la reserva que necesita una decisión.</h2>
        </div>
        <div className="reservation-gallery">
          <aside className="reservation-queue">
          <div className="panel-title">
            <CalendarDays size={18} />
            <h2>Cola de llegadas</h2>
          </div>
          <p className="panel-note">Reservas próximas que conviene revisar antes del cierre operativo.</p>
          {reservations.map((reservation) => (
            <button
              className={`queue-item ${reservation.id === selectedId ? "active" : ""}`}
              key={reservation.id}
              type="button"
              onClick={() => selectReservation(reservation)}
            >
              <span>
                <strong>{reservation.id}</strong>
                <small>{reservation.guest}</small>
              </span>
              <em>{formatArrival(reservation)} · {reservation.status}</em>
            </button>
          ))}
          </aside>

          <article className="reservation-portrait">
            <span>{selectedReservation.id}</span>
            <h3>{selectedReservation.guest}</h3>
            <p>{selectedReservation.stay}</p>
            <dl>
              <div>
                <dt>Llegada</dt>
                <dd>{formatArrival(selectedReservation)}</dd>
              </div>
              <div>
                <dt>Canal</dt>
                <dd>{channelLabels[form.market_segment_type] ?? form.market_segment_type}</dd>
              </div>
              <div>
                <dt>Estancia</dt>
                <dd>{nights} noches</dd>
              </div>
              <div>
                <dt>Valor</dt>
                <dd>{formatCurrency(roomRevenue)}</dd>
              </div>
            </dl>
          </article>
        </div>
      </section>

      <section className="vertical-section two-column">
        <section className="reservation-review">
          <div className="panel-title">
            <BedDouble size={18} />
            <h2>Señales de la reserva</h2>
            <span>{formatArrival(selectedReservation)}</span>
          </div>
          <p className="panel-note">
            Ajusta solo lo imprescindible. Cada cambio recalibra el contexto que usará el motor de predicción.
          </p>

          <div className="form-grid">
            {fieldGroups.map((group) => (
              <fieldset key={group.title}>
                <legend>{group.title}</legend>
                <p>{group.helper}</p>
                {group.fields.map(([name, label, type, options, suffix]) => (
                  <label key={name}>
                    <span>{label}</span>
                    {type === "select" ? (
                      <select value={form[name]} onChange={(event) => updateField(name, event.target.value)}>
                        {options.map((option) => (
                          <option key={option} value={option}>
                            {channelLabels[option] ?? (Number(option) === 1 ? "Sí" : Number(option) === 0 ? "No" : String(option))}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <span className="beta-input-wrap">
                        <input
                          min="0"
                          type="number"
                          value={form[name]}
                          onChange={(event) => updateField(name, Number(event.target.value))}
                        />
                        {suffix && <em>{suffix}</em>}
                      </span>
                    )}
                  </label>
                ))}
              </fieldset>
            ))}
          </div>

          <button className="calculate-button" type="button" onClick={calculateRisk} disabled={isLoading}>
            {isLoading ? "Analizando reserva..." : "Calcular riesgo"}
            <RefreshCw size={17} />
          </button>
        </section>

        <aside className="signal-card">
          <div className="panel-title">
            <TrendingUp size={18} />
            <h2>Lectura de señales</h2>
          </div>
          <p className="panel-note">Una vista simple de las variables que más influyen antes de calcular.</p>
          <div className="signal-bars">
            <span>Antelación</span>
            <i><b style={{ width: `${leadSignal}%` }} /></i>
            <span>Compromiso</span>
            <i><b style={{ width: `${requestSignal}%` }} /></i>
            <span>Precio</span>
            <i><b style={{ width: `${priceSignal}%` }} /></i>
          </div>
        </aside>
      </section>

      <section className="vertical-section decision-section">
        <aside className={`risk-panel ${result?.risk_level ?? "empty"}`}>
          <div className="panel-title">
            <Hotel size={18} />
            <h2>Decisión operativa</h2>
          </div>
          <p className="panel-note">Lectura pensada para decidir si conviene contactar, confirmar o solo observar.</p>

          <div className="risk-score">
            <span>{riskTitle(result)}</span>
            <strong>{probability === null ? "--" : `${probability}%`}</strong>
            <small>
              {result
                ? result.prediction === "Canceled"
                  ? "Probabilidad estimada de cancelación."
                  : "La reserva apunta a mantenerse activa."
                : "Calcula una reserva para activar la recomendación."}
            </small>
          </div>

          {result && (
            <>
              <ul className="risk-factors">
                {result.main_factors.map((factor) => (
                  <li key={factor}>
                    <CheckCircle2 size={16} />
                    {factor}
                  </li>
                ))}
              </ul>
              <p className="recommendation">{result.recommendation}</p>
              <div className="feedback-actions">
                <button type="button" onClick={() => sendFeedback("correct", result.prediction)}>
                  Confirmar lectura
                </button>
                <button type="button" onClick={() => sendFeedback("incorrect")}>
                  Revisar
                </button>
                <button type="button" onClick={() => sendFeedback("unknown")}>
                  Aún no se sabe
                </button>
              </div>
              <p className="feedback-state">
                {feedbackState === "saving" && "Guardando feedback..."}
                {feedbackState === "saved" && "Feedback guardado para seguimiento y mejora del modelo."}
              </p>
            </>
          )}
        </aside>

        <article className="next-action-card">
          <AlertTriangle size={22} />
          <h2>Siguiente mejor acción</h2>
          <p>{riskDescription(result)}</p>
          <small>
            El objetivo no es sustituir el criterio del equipo: es ordenar prioridades antes de la llegada.
          </small>
        </article>
      </section>
    </main>
  );
}
