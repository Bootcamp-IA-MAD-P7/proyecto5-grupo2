import React, { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  BedDouble,
  CalendarDays,
  CheckCircle2,
  ClipboardCheck,
  LoaderCircle,
  RotateCcw,
  Send,
  UserRound
} from "lucide-react";
import { predictReservation, submitPredictionFeedback } from "../services/predictionService";
import "./ReservationEvaluation.css";
import WorkflowSteps from "./WorkflowSteps";

const hotelImages = ["/hotel-suite.jpg", "/hotel-room.jpg", "/hotel-resort.jpg"];

function imageForRoom(roomType) {
  const roomNumber = Number(String(roomType).match(/\d+/)?.[0] || 1);
  return hotelImages[roomNumber % hotelImages.length];
}

const fieldGroups = [
  {
    title: "Reserva",
    icon: ClipboardCheck,
    fields: [
      { name: "lead_time", label: "Antelación", type: "number", min: 0, max: 500, suffix: "días" },
      { name: "avg_price_per_room", label: "Precio medio", type: "number", min: 0, max: 1000, step: 0.01, suffix: "EUR" },
      {
        name: "market_segment_type",
        label: "Canal",
        type: "select",
        options: ["Online", "Offline", "Corporate", "Complementary", "Aviation"]
      },
      {
        name: "type_of_meal_plan",
        label: "Plan de comidas",
        type: "select",
        options: ["Meal Plan 1", "Meal Plan 2", "Meal Plan 3", "Not Selected"]
      },
      {
        name: "room_type_reserved",
        label: "Tipo de habitación",
        type: "select",
        options: [
          "Room_Type 1",
          "Room_Type 2",
          "Room_Type 3",
          "Room_Type 4",
          "Room_Type 5",
          "Room_Type 6",
          "Room_Type 7"
        ]
      },
      { name: "no_of_special_requests", label: "Solicitudes especiales", type: "number", min: 0, max: 10 }
    ]
  },
  {
    title: "Estancia",
    icon: CalendarDays,
    fields: [
      { name: "arrival_year", label: "Año de llegada", type: "number", min: 2017, max: 2030 },
      { name: "arrival_month", label: "Mes", type: "number", min: 1, max: 12 },
      { name: "arrival_date", label: "Día", type: "number", min: 1, max: 31 },
      { name: "no_of_weekend_nights", label: "Noches de fin de semana", type: "number", min: 0, max: 30 },
      { name: "no_of_week_nights", label: "Noches entre semana", type: "number", min: 0, max: 30 }
    ]
  },
  {
    title: "Huésped",
    icon: UserRound,
    fields: [
      { name: "no_of_adults", label: "Adultos", type: "number", min: 1, max: 10 },
      { name: "no_of_children", label: "Niños", type: "number", min: 0, max: 10 },
      { name: "no_of_previous_cancellations", label: "Cancelaciones previas", type: "number", min: 0, max: 30 },
      {
        name: "no_of_previous_bookings_not_canceled",
        label: "Reservas previas mantenidas",
        type: "number",
        min: 0,
        max: 100
      }
    ]
  }
];

const numericFields = new Set(
  fieldGroups.flatMap((group) => group.fields.filter((field) => field.type === "number").map((field) => field.name))
);

function normalizePayload(form) {
  return Object.fromEntries(
    Object.entries(form).map(([name, value]) => [name, numericFields.has(name) ? Number(value) : value])
  );
}

function riskLabel(level) {
  if (level === "high") return "Alto";
  if (level === "medium") return "Medio";
  return "Bajo";
}

function ReservationEvaluation({
  reservation,
  modelInfo,
  onBack,
  onPredictionComplete,
  onFeedbackSaved,
  onNextReservation
}) {
  const [form, setForm] = useState(reservation?.inputData || null);
  const [result, setResult] = useState(reservation?.prediction || null);
  const [isDirty, setIsDirty] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [predictionError, setPredictionError] = useState("");
  const [actualOutcome, setActualOutcome] = useState("");
  const [comments, setComments] = useState("");
  const [feedbackState, setFeedbackState] = useState("idle");
  const [feedbackError, setFeedbackError] = useState("");

  useEffect(() => {
    setForm(reservation?.inputData || null);
    setResult(reservation?.prediction || null);
    setIsDirty(false);
    setPredictionError("");
    setActualOutcome("");
    setComments("");
    setFeedbackState("idle");
    setFeedbackError("");
  }, [reservation]);

  const staySummary = useMemo(() => {
    if (!form) return { nights: 0, value: 0 };
    const nights = Number(form.no_of_weekend_nights) + Number(form.no_of_week_nights);
    return {
      nights,
      value: Math.round(Number(form.avg_price_per_room) * Math.max(nights, 1))
    };
  }, [form]);

  const reservationImage = imageForRoom(form?.room_type_reserved);

  if (!reservation || !form) {
    return (
      <section className="evaluation-empty">
        <h1>No hay una reserva disponible para evaluar</h1>
        <button className="secondary-button" type="button" onClick={onBack}>Volver a operación</button>
      </section>
    );
  }

  function updateField(name, value, type) {
    const nextValue = type === "number" && value !== "" ? Number(value) : value;
    setForm((current) => ({ ...current, [name]: nextValue }));
    setIsDirty(true);
    setFeedbackState("idle");
    setActualOutcome("");
  }

  function resetForm() {
    setForm(reservation.inputData);
    setResult(reservation.prediction);
    setIsDirty(false);
    setPredictionError("");
    setActualOutcome("");
    setComments("");
    setFeedbackState("idle");
  }

  async function calculateRisk(event) {
    event.preventDefault();
    setIsPredicting(true);
    setPredictionError("");
    setFeedbackState("idle");
    setActualOutcome("");

    try {
      const payload = normalizePayload(form);
      const prediction = await predictReservation(payload);
      setForm(payload);
      setResult(prediction);
      setIsDirty(false);
      onPredictionComplete(payload, prediction);
    } catch (error) {
      setPredictionError(error.message || "No se pudo calcular el riesgo.");
    } finally {
      setIsPredicting(false);
    }
  }

  async function sendFeedback() {
    if (!result || !actualOutcome || isDirty) return;

    const actualStatus = actualOutcome === "unknown" ? null : actualOutcome;
    const userFeedback =
      actualStatus === null ? "unknown" : result.prediction === actualStatus ? "correct" : "incorrect";

    setFeedbackState("saving");
    setFeedbackError("");

    try {
      await submitPredictionFeedback({
        input_data: normalizePayload(form),
        prediction: result.prediction,
        probability: result.probability,
        risk_level: result.risk_level,
        model_version: result.model_version,
        user_feedback: userFeedback,
        actual_status: actualStatus,
        comments: comments.trim() || null,
        source: "frontend_ops_unified"
      });
      setFeedbackState("saved");
      await onFeedbackSaved();
    } catch (error) {
      setFeedbackState("error");
      setFeedbackError(error.message || "No se pudo guardar el feedback.");
    }
  }

  const probability = result ? Math.round(Number(result.probability) * 100) : null;
  const actualStatus = actualOutcome === "unknown" ? null : actualOutcome || null;
  const feedbackMatches = actualStatus ? result?.prediction === actualStatus : null;
  const activeWorkflowStep = actualOutcome ? 3 : 2;
  const completedWorkflowStep = feedbackState === "saved" ? 3 : actualOutcome ? 2 : 1;

  return (
    <section className="evaluation-section" aria-labelledby="evaluation-title">
      <WorkflowSteps
        activeStep={activeWorkflowStep}
        completedThrough={completedWorkflowStep}
        onReturnToQueue={onBack}
      />
      <div className="evaluation-heading">
        <button className="back-button" type="button" onClick={onBack}>
          <ArrowLeft size={18} />
          Operación
        </button>
        <div>
          <span className="section-kicker">{reservation.id}</span>
          <h1 id="evaluation-title">Evaluación de reserva</h1>
          <p>{reservation.secondaryLabel}</p>
        </div>
        <div className="evaluation-visual">
          <img src={reservationImage} alt="" />
          <div className="evaluation-context">
            <span><BedDouble size={17} /> {staySummary.nights} noches</span>
            <strong>{staySummary.value.toLocaleString("es-ES")} EUR</strong>
          </div>
        </div>
      </div>

      <div className="evaluation-layout">
        <form className="evaluation-form" onSubmit={calculateRisk}>
          <div className="form-panel-header">
            <div>
              <h2>Variables del Champion</h2>
              <p>Datos requeridos para que el modelo Champion evalúe la reserva.</p>
            </div>
            {isDirty && <span className="dirty-badge">Cambios pendientes</span>}
          </div>

          {fieldGroups.map((group) => {
            const Icon = group.icon;
            return (
              <fieldset key={group.title}>
                <legend><Icon size={18} /> {group.title}</legend>
                <div className="evaluation-field-grid">
                  {group.fields.map((field) => (
                    <label className="evaluation-field" key={field.name}>
                      <span>{field.label}</span>
                      {field.type === "select" ? (
                        <select
                          required
                          value={form[field.name]}
                          onChange={(event) => updateField(field.name, event.target.value, field.type)}
                        >
                          {field.options.map((option) => <option key={option} value={option}>{option}</option>)}
                        </select>
                      ) : (
                        <span className="number-input">
                          <input
                            required
                            type="number"
                            min={field.min}
                            max={field.max}
                            step={field.step || 1}
                            value={form[field.name]}
                            onChange={(event) => updateField(field.name, event.target.value, field.type)}
                          />
                          {field.suffix && <em>{field.suffix}</em>}
                        </span>
                      )}
                    </label>
                  ))}
                </div>
              </fieldset>
            );
          })}

          <div className="binary-options">
            <label>
              <input
                type="checkbox"
                checked={Boolean(Number(form.repeated_guest))}
                onChange={(event) => updateField("repeated_guest", event.target.checked ? 1 : 0, "number")}
              />
              <span>Huésped repetidor</span>
            </label>
            <label>
              <input
                type="checkbox"
                checked={Boolean(Number(form.required_car_parking_space))}
                onChange={(event) => updateField("required_car_parking_space", event.target.checked ? 1 : 0, "number")}
              />
              <span>Requiere plaza de parking</span>
            </label>
          </div>

          {predictionError && <p className="inline-error" role="alert">{predictionError}</p>}

          <div className="form-actions">
            <button className="secondary-button" type="button" onClick={resetForm} disabled={!isDirty}>
              <RotateCcw size={17} />
              Restablecer
            </button>
            <button className="primary-button calculate-risk-button" type="submit" disabled={isPredicting}>
              {isPredicting ? <LoaderCircle className="spin" size={18} /> : <Send size={18} />}
              {isPredicting ? "Calculando..." : "Calcular riesgo"}
            </button>
          </div>
        </form>

        <aside className="decision-panel">
          <header>
            <span>Decisión operativa</span>
            <small>{result?.model_version || modelInfo?.model_version || "Modelo no disponible"}</small>
          </header>

          {result ? (
            <>
              <div className={`decision-score ${result.risk_level}`}>
                <div>
                  <span>Riesgo {riskLabel(result.risk_level).toLowerCase()}</span>
                  <strong>{probability}%</strong>
                </div>
                <p>{result.prediction === "Canceled" ? "Posible cancelación" : "Reserva probablemente estable"}</p>
              </div>

              {isDirty && (
                <div className="stale-result">El resultado corresponde a los valores anteriores. Recalcula para actualizarlo.</div>
              )}

              <section className="decision-block">
                <h2>Factores principales</h2>
                <ul>
                  {result.main_factors.map((factor) => (
                    <li key={factor}><CheckCircle2 size={16} /> {factor}</li>
                  ))}
                </ul>
              </section>

              <section className="decision-block recommendation-block">
                <h2>Recomendación</h2>
                <p>{result.recommendation}</p>
              </section>

              <section className={`feedback-block ${isDirty ? "disabled" : ""}`}>
                <div className="feedback-heading">
                  <h2>Resultado observado</h2>
                  <span>Registro de seguimiento</span>
                </div>
                <div className="outcome-options" role="group" aria-label="Resultado real de la reserva">
                  <button
                    type="button"
                    className={actualOutcome === "Canceled" ? "active" : ""}
                    onClick={() => { setActualOutcome("Canceled"); setFeedbackState("idle"); }}
                    disabled={isDirty || feedbackState === "saving"}
                  >
                    Cancelada
                  </button>
                  <button
                    type="button"
                    className={actualOutcome === "Not_Canceled" ? "active" : ""}
                    onClick={() => { setActualOutcome("Not_Canceled"); setFeedbackState("idle"); }}
                    disabled={isDirty || feedbackState === "saving"}
                  >
                    Mantenida
                  </button>
                  <button
                    type="button"
                    className={actualOutcome === "unknown" ? "active" : ""}
                    onClick={() => { setActualOutcome("unknown"); setFeedbackState("idle"); }}
                    disabled={isDirty || feedbackState === "saving"}
                  >
                    Aún no se sabe
                  </button>
                </div>

                {actualOutcome && actualOutcome !== "unknown" && (
                  <p className={`feedback-preview ${feedbackMatches ? "correct" : "incorrect"}`}>
                    {feedbackMatches ? "El resultado confirma la predicción." : "El resultado contradice la predicción."}
                  </p>
                )}

                <label className="feedback-comments">
                  <span>Comentario opcional</span>
                  <textarea
                    maxLength="500"
                    value={comments}
                    onChange={(event) => setComments(event.target.value)}
                    placeholder="Contexto útil para seguimiento"
                    disabled={isDirty || feedbackState === "saving"}
                  />
                </label>

                {feedbackError && <p className="inline-error" role="alert">{feedbackError}</p>}
                {feedbackState === "saved" && (
                  <div className="feedback-complete">
                    <p className="feedback-saved">Feedback guardado correctamente.</p>
                    {onNextReservation && (
                      <button type="button" onClick={onNextReservation}>
                        Siguiente reserva
                        <ArrowRight size={17} />
                      </button>
                    )}
                  </div>
                )}

                <button
                  className="feedback-submit"
                  type="button"
                  onClick={sendFeedback}
                  disabled={!actualOutcome || isDirty || feedbackState === "saving" || feedbackState === "saved"}
                >
                  {feedbackState === "saving" ? <LoaderCircle className="spin" size={17} /> : <ClipboardCheck size={17} />}
                  {feedbackState === "saving" ? "Guardando..." : "Guardar feedback"}
                </button>
              </section>
            </>
          ) : (
            <div className="decision-empty">Calcula el riesgo para obtener la decisión operativa.</div>
          )}
        </aside>
      </div>
    </section>
  );
}

export default ReservationEvaluation;
