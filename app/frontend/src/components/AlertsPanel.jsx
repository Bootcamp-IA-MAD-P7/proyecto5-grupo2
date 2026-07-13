import React, { useEffect, useState, Fragment } from "react";
import ReservationDetailModal from "./ReservationDetailModal";
import { fetchPredictedReservations } from "../services/predictionService";
import "./AlertsPanel.css";

function AlertsPanel() {
  const [selectedReservation, setSelectedReservation] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [isLoadingAlerts, setIsLoadingAlerts] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadAlerts() {
      setIsLoadingAlerts(true);
      setError("");
      try {
        const reservations = await fetchPredictedReservations(12);
        const highRiskReservations = reservations.filter((reservation) => reservation.riskLevel === "high");
        if (isMounted) {
          setAlerts(highRiskReservations);
        }
      } catch {
        if (isMounted) {
          setError("No se pudieron cargar las alertas reales del backend.");
        }
      } finally {
        if (isMounted) {
          setIsLoadingAlerts(false);
        }
      }
    }

    loadAlerts();

    return () => {
      isMounted = false;
    };
  }, []);

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
        <p>
          {isLoadingAlerts
            ? "Cargando alertas reales..."
            : `${alerts.length} reservas requieren acción inmediata`}
        </p>
        {error && <p>{error}</p>}
      </div>

      <div className="alerts-list">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className="alert-card alert-card-clickable"
            onClick={() => setSelectedReservation(alert)}
          >
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
