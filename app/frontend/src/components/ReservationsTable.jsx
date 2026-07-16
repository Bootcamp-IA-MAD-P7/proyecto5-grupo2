import React, { useMemo, useState } from "react";
import { ArrowRight, Eye, Search } from "lucide-react";
import "./ReservationsTable.css";

const riskOrder = { high: 3, medium: 2, low: 1 };

function formatDate(dateString) {
  return new Date(`${dateString}T00:00:00`).toLocaleDateString("es-ES", {
    day: "2-digit",
    month: "short",
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
  if (level === "high") return "Alto";
  if (level === "medium") return "Medio";
  return "Bajo";
}

function ReservationsTable({ reservations, isLoading, onSelect, onEvaluate }) {
  const [riskFilter, setRiskFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [sortBy, setSortBy] = useState("risk");

  const visibleReservations = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    const filtered = reservations.filter((reservation) => {
      const matchesRisk = riskFilter === "all" || reservation.riskLevel === riskFilter;
      const matchesQuery =
        !normalizedQuery ||
        reservation.id.toLowerCase().includes(normalizedQuery) ||
        reservation.secondaryLabel.toLowerCase().includes(normalizedQuery) ||
        reservation.status.toLowerCase().includes(normalizedQuery);
      return matchesRisk && matchesQuery;
    });

    return [...filtered].sort((a, b) => {
      if (sortBy === "arrival") return a.arrival.localeCompare(b.arrival);
      if (sortBy === "value") return b.estimatedStayValue - a.estimatedStayValue;
      return riskOrder[b.riskLevel] - riskOrder[a.riskLevel] || b.riskPercent - a.riskPercent;
    });
  }, [query, reservations, riskFilter, sortBy]);

  return (
    <div className="reservations-tool">
      <div className="table-toolbar">
        <div className="table-heading">
          <h2>Todas las reservas</h2>
          <span>{isLoading ? "Cargando" : `${visibleReservations.length} visibles`}</span>
        </div>

        <label className="search-field">
          <Search size={17} />
          <span className="sr-only">Filtrar la página actual</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filtrar esta página"
          />
        </label>

        <div className="risk-filter" aria-label="Filtrar por riesgo">
          {["all", "high", "medium", "low"].map((level) => (
            <button
              key={level}
              type="button"
              className={riskFilter === level ? "active" : ""}
              onClick={() => setRiskFilter(level)}
            >
              {level === "all" ? "Todas" : riskLabel(level)}
            </button>
          ))}
        </div>

        <label className="sort-field">
          <span>Ordenar</span>
          <select value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
            <option value="risk">Mayor riesgo</option>
            <option value="arrival">Fecha de llegada</option>
            <option value="value">Valor de estancia</option>
          </select>
        </label>
      </div>

      <div className="table-scroll">
        <table className="reservations-table">
          <thead>
            <tr>
              <th>Reserva</th>
              <th>Contexto</th>
              <th>Llegada</th>
              <th>Estancia</th>
              <th>Valor estimado</th>
              <th>Riesgo estimado</th>
              <th><span className="sr-only">Acciones</span></th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td className="table-state" colSpan="7">Analizando datos de las reservas...</td>
              </tr>
            ) : visibleReservations.length === 0 ? (
              <tr>
                <td className="table-state" colSpan="7">No hay reservas que coincidan con los filtros.</td>
              </tr>
            ) : (
              visibleReservations.map((reservation) => (
                <tr key={reservation.id} onClick={() => onSelect(reservation)}>
                  <td>
                    <div className="reservation-identity">
                      <span>{reservation.id.slice(-2)}</span>
                      <div>
                        <strong>{reservation.guest}</strong>
                        <small>{reservation.id}</small>
                      </div>
                    </div>
                  </td>
                  <td>
                    <strong className="context-label">{reservation.secondaryLabel}</strong>
                    <small className="row-secondary">{reservation.status}</small>
                  </td>
                  <td>
                    <strong>{formatDate(reservation.arrival)}</strong>
                    <small className="row-secondary">registro histórico</small>
                  </td>
                  <td>{reservation.nights} {reservation.nights === 1 ? "noche" : "noches"}</td>
                  <td>{formatCurrency(reservation.estimatedStayValue)}</td>
                  <td>
                    <span className={`risk-badge ${reservation.riskLevel}`}>
                      {reservation.riskPercent}% · {riskLabel(reservation.riskLevel)}
                    </span>
                  </td>
                  <td>
                    <div className="row-actions">
                      <button
                        className="row-icon-button"
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          onSelect(reservation);
                        }}
                        aria-label={`Ver detalle de ${reservation.id}`}
                        title="Ver detalle"
                      >
                        <Eye size={18} />
                      </button>
                      <button
                        className="evaluate-button"
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          onEvaluate(reservation);
                        }}
                      >
                        Evaluar
                        <ArrowRight size={17} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ReservationsTable;
