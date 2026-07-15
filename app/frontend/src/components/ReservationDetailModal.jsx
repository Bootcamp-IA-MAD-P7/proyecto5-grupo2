import React, { useEffect } from "react";
import {
  ArrowRight,
  CalendarDays,
  CircleDollarSign,
  Clock3,
  Lightbulb,
  TrendingUp,
  X
} from "lucide-react";
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

  const riskFactors = reservation.riskFactors || [];
  const strongestImpact = riskFactors[0]?.impact_percentage_points || 1;

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

        <section className="detail-section risk-driver-section">
          <div className="risk-driver-heading">
            <div>
              <TrendingUp size={18} />
              <h3>Qué está elevando el riesgo</h3>
            </div>
            <span>Estimación local</span>
          </div>

          {riskFactors.length > 0 ? (
            <ol className="risk-driver-list">
              {riskFactors.map((factor, index) => (
                <li className={index === 0 ? "primary" : ""} key={factor.feature}>
                  <div className="risk-driver-topline">
                    <span>{index === 0 ? "Mayor impacto" : `Prioridad ${index + 1}`}</span>
                    <strong>+{factor.impact_percentage_points.toFixed(1)} pp</strong>
                  </div>
                  <h4>{factor.label}</h4>
                  <div className="risk-driver-comparison">
                    <span>Actual <strong>{factor.current_value}</strong></span>
                    <span>Referencia <strong>{factor.reference_value}</strong></span>
                  </div>
                  <div className="risk-impact-track" aria-hidden="true">
                    <span
                      style={{
                        width: `${Math.max(
                          12,
                          (factor.impact_percentage_points / strongestImpact) * 100
                        )}%`
                      }}
                    />
                  </div>
                  <p>
                    <Lightbulb size={16} />
                    <span><strong>Acción sugerida:</strong> {factor.action}</span>
                  </p>
                </li>
              ))}
            </ol>
          ) : (
            <div className="risk-driver-empty">
              <p>No se detecta una variable dominante frente al histórico de referencia.</p>
              <ul>
                {reservation.mainFactors.map((factor) => <li key={factor}>{factor}</li>)}
              </ul>
            </div>
          )}

          <small className="risk-method-note">
            El impacto compara esta reserva con valores habituales de reservas no canceladas.
            Sirve para priorizar la revisión y no implica causalidad.
          </small>
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
