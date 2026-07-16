import React, { useMemo } from "react";
import { AlertTriangle, ArrowRight, CalendarDays, CircleDollarSign, Eye } from "lucide-react";
import "./AlertsPanel.css";

const hotelImages = ["/hotel-room.jpg", "/hotel-suite.jpg", "/hotel-resort.jpg"];

function formatDate(dateString) {
  return new Date(`${dateString}T00:00:00`).toLocaleDateString("es-ES", {
    day: "2-digit",
    month: "long",
    year: "numeric"
  });
}

function formatCurrency(value) {
  return new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0
  }).format(value);
}

function AlertsPanel({ reservations, isLoading, onSelect, onEvaluate }) {
  const priorityReservations = useMemo(
    () =>
      reservations
        .filter((reservation) => reservation.riskLevel === "high")
        .sort((a, b) => b.riskPercent - a.riskPercent),
    [reservations]
  );

  return (
    <section className="priority-section" aria-labelledby="priority-title">
      <div className="priority-heading">
        <div>
          <span className="priority-label"><AlertTriangle size={16} /> Riesgo alto</span>
          <h2 id="priority-title">Reservas prioritarias</h2>
        </div>
        <p>{isLoading ? "Evaluando reservas..." : `${priorityReservations.length} requieren revisión`}</p>
      </div>

      {isLoading ? (
        <div className="priority-empty">Calculando prioridades a partir de los datos...</div>
      ) : priorityReservations.length === 0 ? (
        <div className="priority-empty">No hay reservas de riesgo alto en la muestra cargada.</div>
      ) : (
        <div className="priority-grid">
          {priorityReservations.map((reservation, index) => (
            <article className="priority-card" key={reservation.id}>
              <div className="priority-card-media" aria-hidden="true">
                <img src={hotelImages[index % hotelImages.length]} alt="" />
              </div>
              <div className="priority-card-header">
                <div>
                  <small>{reservation.id}</small>
                  <h3>{reservation.guest}</h3>
                  <p>{reservation.secondaryLabel}</p>
                </div>
                <span>{reservation.riskPercent}%</span>
              </div>

              <dl className="priority-facts">
                <div>
                  <dt><CalendarDays size={16} /> Llegada histórica</dt>
                  <dd>{formatDate(reservation.arrival)}</dd>
                </div>
                <div>
                  <dt><CircleDollarSign size={16} /> Valor estimado</dt>
                  <dd>{formatCurrency(reservation.estimatedStayValue)}</dd>
                </div>
              </dl>

              <div className="priority-recommendation">
                <strong>Siguiente acción</strong>
                <p>{reservation.recommendation}</p>
              </div>

              <div className="priority-actions">
                <button type="button" className="secondary-button" onClick={() => onSelect(reservation)}>
                  <Eye size={17} />
                  Ver detalle
                </button>
                <button type="button" className="primary-button" onClick={() => onEvaluate(reservation)}>
                  Evaluar
                  <ArrowRight size={17} />
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default AlertsPanel;
