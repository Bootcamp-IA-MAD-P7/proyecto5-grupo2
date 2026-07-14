import React, { useEffect } from "react";
import { ArrowRight, CalendarDays, CircleDollarSign, Clock3, X } from "lucide-react";
import "./ReservationDetailModal.css";

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

function riskLabel(level) {
  if (level === "high") return "Riesgo alto";
  if (level === "medium") return "Riesgo medio";
  return "Riesgo bajo";
}

function ReservationDetailModal({ reservation, onClose, onEvaluate }) {
  useEffect(() => {
    function handleEscape(event) {
      if (event.key === "Escape") onClose();
    }

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [onClose]);

  if (!reservation) return null;

  return (
    <div className="detail-layer" role="presentation">
      <button className="detail-overlay" type="button" onClick={onClose} aria-label="Cerrar detalle" />
      <aside className="detail-panel" role="dialog" aria-modal="true" aria-labelledby="detail-title">
        <header className="detail-header">
          <div>
            <span className="detail-kicker">{reservation.id}</span>
            <h2 id="detail-title">{reservation.guest}</h2>
            <p>{reservation.secondaryLabel}</p>
          </div>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Cerrar" title="Cerrar">
            <X size={20} />
          </button>
        </header>

        <div className={`detail-risk ${reservation.riskLevel}`}>
          <span>{riskLabel(reservation.riskLevel)}</span>
          <strong>{reservation.riskPercent}%</strong>
          <small>{reservation.prediction.prediction === "Canceled" ? "Cancelación estimada" : "Permanencia estimada"}</small>
        </div>

        <dl className="detail-facts">
          <div>
            <dt><CalendarDays size={16} /> Llegada histórica</dt>
            <dd>{formatDate(reservation.arrival)}</dd>
          </div>
          <div>
            <dt><Clock3 size={16} /> Estancia</dt>
            <dd>{reservation.nights} {reservation.nights === 1 ? "noche" : "noches"}</dd>
          </div>
          <div>
            <dt><CircleDollarSign size={16} /> Valor estimado</dt>
            <dd>{formatCurrency(reservation.estimatedStayValue)}</dd>
          </div>
          <div>
            <dt>Estado de revisión</dt>
            <dd>{reservation.status}</dd>
          </div>
        </dl>

        <section className="detail-section">
          <h3>Factores principales</h3>
          <ul>
            {reservation.mainFactors.map((factor) => <li key={factor}>{factor}</li>)}
          </ul>
        </section>

        <section className="detail-section recommendation-section">
          <h3>Recomendación operativa</h3>
          <p>{reservation.recommendation}</p>
        </section>

        <div className="detail-model">
          <span>Modelo utilizado</span>
          <strong>{reservation.prediction.model_version}</strong>
        </div>

        <footer className="detail-footer">
          <button className="secondary-button" type="button" onClick={onClose}>Cerrar</button>
          <button className="primary-button" type="button" onClick={onEvaluate}>
            Editar y recalcular
            <ArrowRight size={17} />
          </button>
        </footer>
      </aside>
    </div>
  );
}

export default ReservationDetailModal;
