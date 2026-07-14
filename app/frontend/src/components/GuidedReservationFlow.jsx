import React, { useMemo } from "react";
import {
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  CircleDollarSign,
  Eye,
  ListChecks,
  Sparkles
} from "lucide-react";
import "./GuidedReservationFlow.css";

const hotelImages = ["/hotel-suite.jpg", "/hotel-room.jpg", "/hotel-resort.jpg"];

function imageForReservation(reservation) {
  const imageIndex = [...reservation.id].reduce((total, character) => total + character.charCodeAt(0), 0);
  return hotelImages[imageIndex % hotelImages.length];
}

function formatArrival(value) {
  if (!value) return "Fecha no disponible";
  return new Intl.DateTimeFormat("es-ES", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  }).format(new Date(`${value}T12:00:00`));
}

function formatCurrency(value) {
  return new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0
  }).format(Number(value || 0));
}

function riskLabel(level) {
  if (level === "high") return "Alto";
  if (level === "medium") return "Medio";
  return "Bajo";
}

function GuidedReservationFlow({
  isLoading,
  onEvaluate,
  onOpenDetail,
  onSelect,
  reservations,
  selectedReservation
}) {
  const orderedReservations = useMemo(
    () => [...reservations].sort((a, b) => b.riskPercent - a.riskPercent),
    [reservations]
  );

  if (isLoading) {
    return (
      <section className="guided-flow guided-flow-loading" aria-live="polite">
        <Sparkles className="spin" size={21} />
        Evaluando reservas con el Champion...
      </section>
    );
  }

  if (!selectedReservation || orderedReservations.length === 0) {
    return <section className="guided-flow guided-flow-empty">No hay reservas disponibles.</section>;
  }

  const selectedImage = imageForReservation(selectedReservation);

  return (
    <section className="guided-flow" aria-labelledby="guided-flow-title">
      <header className="guided-flow-header">
        <div>
          <span className="section-kicker">Cola priorizada</span>
          <h2 id="guided-flow-title">Revisión guiada</h2>
        </div>
        <span className="guided-flow-count">{orderedReservations.length} reservas</span>
      </header>

      <div className="guided-flow-layout">
        <aside className="guided-queue" aria-label="Cola de reservas por riesgo">
          <header>
            <ListChecks size={19} />
            <div>
              <strong>Prioridad Champion</strong>
              <small>Mayor riesgo primero</small>
            </div>
          </header>

          <div className="guided-queue-list">
            {orderedReservations.map((reservation, index) => (
              <button
                type="button"
                className={selectedReservation.id === reservation.id ? "active" : ""}
                key={reservation.id}
                onClick={() => onSelect(reservation)}
                aria-pressed={selectedReservation.id === reservation.id}
              >
                <span className="queue-rank">{index + 1}</span>
                <span className="queue-copy">
                  <strong>{reservation.guest}</strong>
                  <small>{formatArrival(reservation.arrival)} · histórico</small>
                </span>
                <span className={`queue-risk ${reservation.riskLevel}`}>
                  {reservation.riskPercent}%
                </span>
              </button>
            ))}
          </div>
        </aside>

        <article className="guided-selection">
          <header>
            <div>
              <span>Reserva seleccionada</span>
              <strong>{selectedReservation.id}</strong>
            </div>
            <span className={`guided-risk-badge ${selectedReservation.riskLevel}`}>
              Riesgo {riskLabel(selectedReservation.riskLevel)} · {selectedReservation.riskPercent}%
            </span>
          </header>

          <div className="guided-selection-media" aria-hidden="true">
            <img src={selectedImage} alt="" />
          </div>

          <div className="guided-identity">
            <span className="guided-avatar">{selectedReservation.id.slice(-2)}</span>
            <div>
              <h3>{selectedReservation.guest}</h3>
              <p>{selectedReservation.secondaryLabel}</p>
            </div>
          </div>

          <dl className="guided-facts">
            <div>
              <dt><CalendarDays size={16} /> Llegada</dt>
              <dd>{formatArrival(selectedReservation.arrival)}</dd>
              <small>registro histórico</small>
            </div>
            <div>
              <dt><CircleDollarSign size={16} /> Valor estimado</dt>
              <dd>{formatCurrency(selectedReservation.estimatedStayValue)}</dd>
              <small>{selectedReservation.nights} noches</small>
            </div>
          </dl>

          <section className="guided-signals">
            <h3>Señales principales</h3>
            <ul>
              {(selectedReservation.mainFactors || []).map((factor) => (
                <li key={factor}>
                  <CheckCircle2 size={16} />
                  {factor}
                </li>
              ))}
            </ul>
          </section>

          <section className="guided-recommendation">
            <span>Siguiente acción recomendada</span>
            <p>{selectedReservation.recommendation}</p>
          </section>

          <footer>
            <button className="guided-detail-button" type="button" onClick={() => onOpenDetail(selectedReservation)}>
              <Eye size={18} />
              Ver detalle
            </button>
            <button className="guided-evaluate-button" type="button" onClick={() => onEvaluate(selectedReservation)}>
              Continuar evaluación
              <ArrowRight size={18} />
            </button>
          </footer>
        </article>
      </div>
    </section>
  );
}

export default GuidedReservationFlow;
