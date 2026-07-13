import React, { useState, Fragment } from "react";
import ReservationDetailModal from "./ReservationDetailModal";
import { mockAlerts } from "../data/mockReservations";
import "./AlertsPanel.css";

function AlertsPanel() {
  const [selectedReservation, setSelectedReservation] = useState(null);
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric"
    });
  }

  return (
    <Fragment>
       {selectedReservation && (
        <ReservationDetailModal
          reservation={selectedReservation}
          onClose={() => setSelectedReservation(null)}
        />
      )}
      <div className="alerts-bg" />
      <div className="alerts-bg-overlay" />
      <div className="alerts-page">
      <div className="alerts-header">
        <h2>
          <span className="alert-dot" />
          Alertas Urgentes
        </h2>
        <p>{mockAlerts.length} reservas requieren acción inmediata</p>
      </div>

      <div className="alerts-list">
        {mockAlerts.map((alert) => (
          <div key={alert.id} className="alert-card" onClick={() => setSelectedReservation(alert)} style={{ cursor: "pointer" }}>
            <div className="alert-card-header">
              <div className="alert-guest">
                <div className="alert-avatar">
                  {alert.guest.split(" ").map((n) => n[0]).join("")}
                </div>
                <div>
                  <div className="alert-name">{alert.guest}</div>
                  <div className="alert-email">{alert.email}</div>
                  <div className="alert-arrival">
                    {formatDate(alert.arrival)} · {alert.nights} {alert.nights === 1 ? "noche" : "noches"}
                  </div>
                  <div className="alert-urgency">Llega en {alert.daysLeft} {alert.daysLeft === 1 ? "día" : "días"}</div>
                </div>
              </div>
              <div className="alert-risk">
                <div className="alert-risk-percent">{alert.riskPercent}%</div>
                <div className="alert-risk-label">RIESGO ALTO</div>
              </div>
            </div>

            <div className="alert-actions">
              <button className="btn-email">Enviar email</button>
              <button className="btn-call">Llamar</button>
              <button className="btn-detail">Ver detalle</button>
            </div>
          </div>
        ))}
      </div>
    </div>
    </Fragment>
  );
}

export default AlertsPanel;
