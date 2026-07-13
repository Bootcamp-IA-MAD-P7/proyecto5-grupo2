import React, { Fragment, useState } from "react";
import { submitPredictionFeedback } from "../services/predictionService";
import "./ReservationDetailModal.css";

function ReservationDetailModal({ reservation, onClose }) {
  const [feedbackState, setFeedbackState] = useState("idle");

  if (!reservation) return null;

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric"
    });
  }

  async function sendFeedback(userFeedback, actualStatus) {
    if (!reservation.inputData || !reservation.prediction) return;

    setFeedbackState("saving");
    try {
      await submitPredictionFeedback({
        input_data: reservation.inputData,
        prediction: reservation.prediction.prediction,
        probability: reservation.prediction.probability,
        risk_level: reservation.prediction.risk_level,
        model_version: reservation.prediction.model_version,
        user_feedback: userFeedback,
        actual_status: actualStatus,
        comments: `Feedback desde modal para ${reservation.id}`,
        source: "develop_frontend"
      });
      setFeedbackState("saved");
    } catch {
      setFeedbackState("error");
    }
  }

  const riskLabel = reservation.riskLevel === "high" ? "ALTO" : reservation.riskLevel === "medium" ? "MEDIO" : "BAJO";
  const factors = reservation.mainFactors?.length ? reservation.mainFactors : ["Patrón de reserva evaluado por el modelo"];

  return (
    <Fragment>
      <div className="modal-overlay" onClick={onClose} />

      <div className="modal-panel">
        <div className="modal-header">
          <h3>Detalle de Reserva</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-guest">
          <div className="modal-avatar">
            {reservation.guest.split(" ").map((n) => n[0]).join("")}
          </div>
          <div>
            <div className="modal-name">{reservation.guest}</div>
            <div className="modal-email">{reservation.email}</div>
          </div>
        </div>

        <div className="modal-info-grid">
          <div className="modal-info-item">
            <div className="modal-info-label">Llegada</div>
            <div className="modal-info-value">{formatDate(reservation.arrival)}</div>
          </div>
          <div className="modal-info-item">
            <div className="modal-info-label">Noches</div>
            <div className="modal-info-value">{reservation.nights} {reservation.nights === 1 ? "noche" : "noches"}</div>
          </div>
          <div className="modal-info-item">
            <div className="modal-info-label">Precio</div>
            <div className="modal-info-value">{reservation.price} EUR</div>
          </div>
          <div className="modal-info-item risk">
            <div className="modal-info-label">Riesgo</div>
            <div className="modal-info-value modal-info-value-risk">
              {reservation.riskPercent}% {riskLabel}
            </div>
          </div>
        </div>

        <div className="modal-section">
          <div className="modal-section-title">FACTORES DE RIESGO</div>
          <div className="modal-factors">
            {factors.map((factor) => (
              <div className="modal-factor" key={factor}>
                <span className="modal-factor-dot" />
                {factor}
              </div>
            ))}
          </div>
        </div>

        <div className="modal-section">
          <div className="modal-section-title">RECOMENDACIÓN</div>
          <div className="modal-recommendation">
            {reservation.recommendation}
          </div>
        </div>

        <div className="modal-actions">
          <button
            className="modal-btn-email"
            onClick={() => window.open(`mailto:?subject=Confirmación de reserva - Hotel Insights&body=Hola,%0D%0A%0D%0AQueremos confirmar la reserva ${reservation.id} para el ${formatDate(reservation.arrival)}.%0D%0A%0D%0ASaludos cordiales,%0D%0AHotel Insights`)}
          >
            Enviar email
          </button>
          <button
            className="modal-btn-call"
            onClick={() => window.open("tel:+34123456789")}
          >
            Llamar
          </button>
        </div>

        <div className="modal-section">
          <div className="modal-section-title">FEEDBACK DE PREDICCIÓN</div>
          <div className="modal-feedback-note">
            {feedbackState === "saved"
              ? "Feedback guardado correctamente."
              : feedbackState === "error"
                ? "No se pudo guardar el feedback."
                : "Registra si la predicción fue correcta para mejorar el seguimiento."}
          </div>
          <div className="modal-feedback">
            <button
              className="modal-btn-yes"
              disabled={feedbackState === "saving"}
              onClick={() => sendFeedback("correct", "Canceled")}
            >
              Sí, se canceló
            </button>
            <button
              className="modal-btn-no"
              disabled={feedbackState === "saving"}
              onClick={() => sendFeedback("correct", "Not_Canceled")}
            >
              No, llegó bien
            </button>
          </div>
        </div>
      </div>
    </Fragment>
  );
}

export default ReservationDetailModal;
