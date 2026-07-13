import React, { Fragment } from "react";
import "./ReservationDetailModal.css";

function ReservationDetailModal({ reservation, onClose }) {
  if (!reservation) return null;

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric"
    });
  }

  function daysUntilArrival(dateString) {
    const arrival = new Date(dateString);
    const today = new Date();
    const diffTime = arrival - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  }

  return (
    <Fragment>
      {/* Overlay oscuro */}
      <div className="modal-overlay" onClick={onClose} />
      
      {/* Panel lateral */}
      <div className="modal-panel">
        {/* Header */}
        <div className="modal-header">
          <h3>Detalle de Reserva</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        {/* Info del huésped */}
        <div className="modal-guest">
          <div className="modal-avatar">
            {reservation.guest.split(" ").map((n) => n[0]).join("")}
          </div>
          <div>
            <div className="modal-name">{reservation.guest}</div>
            <div className="modal-email">{reservation.email}</div>
          </div>
        </div>

        {/* Grid de info */}
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
              {reservation.riskPercent}% ALTO
            </div>
          </div>
        </div>

        {/* Factores de riesgo */}
        <div className="modal-section">
          <div className="modal-section-title">FACTORES DE RIESGO</div>
          <div className="modal-factors">
            <div className="modal-factor">
              <span className="modal-factor-dot" />
              Lead time elevado
            </div>
            <div className="modal-factor">
              <span className="modal-factor-dot" />
              Sin solicitudes especiales
            </div>
            <div className="modal-factor">
              <span className="modal-factor-dot" />
              Canal online
            </div>
          </div>
        </div>

        {/* Recomendación */}
        <div className="modal-section">
          <div className="modal-section-title">RECOMENDACIÓN</div>
          <div className="modal-recommendation">
            Contactar proactivamente para confirmar la reserva. Ofrecer upgrade de habitación para aumentar compromiso.
          </div>
        </div>

        {/* Botones de acción */}
        <div className="modal-actions">
          <button 
            className="modal-btn-email" 
            onClick={() => window.open(`mailto:${reservation.email}?subject=Confirmación de reserva - Hotel Insights&body=Hola ${reservation.guest},%0D%0A%0D%0AQueremos confirmar su reserva para el ${formatDate(reservation.arrival)}.%0D%0A%0D%0ASaludos cordiales,%0D%0AHotel Insights`)}
          >
            Enviar email
          </button>
          <button 
            className="modal-btn-call" 
            onClick={() => window.open(`tel:+34123456789`)}
          >
            Llamar
          </button>
        </div>

        {/* Feedback */}
        <div className="modal-section">
          <div className="modal-section-title">¿LA PREDICCIÓN FUE CORRECTA?</div>
          <div className="modal-feedback">
            <button className="modal-btn-yes">Sí, se canceló</button>
            <button className="modal-btn-no">No, llegó bien</button>
          </div>
        </div>
      </div>
    </Fragment>
  );
}

export default ReservationDetailModal;
