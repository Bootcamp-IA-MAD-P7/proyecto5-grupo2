/* =============================================================================
   RESERVATIONS TABLE - HOTEL INSIGHTS
   =============================================================================
   Tabla de reservas con riesgo de cancelación.
   Ahora usa datos mock (ficticios), luego se conectará con el backend.
   
   RAMA: feature/frontend-reservations-table
   ============================================================================= */

import React, { useState, Fragment  } from "react";
import ReservationDetailModal from "./ReservationDetailModal";
import "./ReservationsTable.css";

/* =============================================================================
   DATOS MOCK (ficticios) - Estos vendrán del backend luego
   =============================================================================
   Cada reserva tiene:
   - id: identificador único
   - guest: nombre del huésped
   - email: correo electrónico
   - arrival: fecha de llegada
   - nights: noches de estancia
   - price: precio total
   - riskLevel: "high" | "medium" | "low"
   - riskPercent: número del 0 al 100
   - status: estado de la reserva
   ============================================================================= */
const mockReservations = [
  {
    id: "RES-2026-0847",
    guest: "María García",
    email: "m.garcia@email.com",
    arrival: "2026-07-15",
    nights: 3,
    price: 450,
    riskLevel: "high",
    riskPercent: 82,
    status: "confirmed"
  },
  {
    id: "RES-2026-0848",
    guest: "Juan López",
    email: "j.lopez@email.com",
    arrival: "2026-07-18",
    nights: 2,
    price: 280,
    riskLevel: "low",
    riskPercent: 15,
    status: "confirmed"
  },
  {
    id: "RES-2026-0849",
    guest: "Anna Smith",
    email: "a.smith@email.com",
    arrival: "2026-07-20",
    nights: 5,
    price: 890,
    riskLevel: "medium",
    riskPercent: 45,
    status: "confirmed"
  },
  {
    id: "RES-2026-0850",
    guest: "Carlos Martínez",
    email: "c.martinez@email.com",
    arrival: "2026-07-22",
    nights: 1,
    price: 120,
    riskLevel: "high",
    riskPercent: 76,
    status: "confirmed"
  },
  {
    id: "RES-2026-0851",
    guest: "Laura Fernández",
    email: "l.fernandez@email.com",
    arrival: "2026-07-25",
    nights: 4,
    price: 560,
    riskLevel: "low",
    riskPercent: 22,
    status: "confirmed"
  }
];

/* =============================================================================
   COMPONENTE RESERVATIONS TABLE
   ============================================================================= */
function ReservationsTable() {
  // ---------------------------------------------------------------------------
  // ESTADO: Filtro activo ("all", "high", "medium", "low")
  // ---------------------------------------------------------------------------
  const [filter, setFilter] = useState("all");
  const [selectedReservation, setSelectedReservation] = useState(null);

  // ---------------------------------------------------------------------------
  // FILTRAR RESERVAS según el botón pulsado
  // ---------------------------------------------------------------------------
  const filteredReservations = mockReservations.filter((reservation) => {
    if (filter === "all") return true;
    return reservation.riskLevel === filter;
  });

  // ---------------------------------------------------------------------------
  // FUNCION: Formatear fecha (2026-07-15 → 15/07/2026)
  // ---------------------------------------------------------------------------
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric"
    });
  }

  // ---------------------------------------------------------------------------
  // FUNCION: Calcular días hasta llegada
  // ---------------------------------------------------------------------------
  function daysUntilArrival(dateString) {
    const arrival = new Date(dateString);
    const today = new Date();
    const diffTime = arrival - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  }

  // ---------------------------------------------------------------------------
  // RENDER
  // ---------------------------------------------------------------------------
  return (
  
    <Fragment>
      {selectedReservation && (
        <ReservationDetailModal
          reservation={selectedReservation}
          onClose={() => setSelectedReservation(null)}
        />
      )}
      <div className="reservations-bg" />
      <div className="reservations-bg-overlay" />
      <div className="reservations-page">
      {/* =====================================================================
          HEADER: Título + filtros
          ===================================================================== */}
      <div className="reservations-header">
        <div>
          <h2>Reservas Entrantes</h2>
          <p>{filteredReservations.length} reservas · {mockReservations.filter(r => r.riskLevel === "high").length} requieren atención</p>
        </div>
        
        {/* Botones de filtro */}
        <div className="filter-buttons">
          <button 
            className={filter === "all" ? "active" : ""} 
            onClick={() => setFilter("all")}
          >
            Todas
          </button>
          <button 
            className={filter === "high" ? "active" : ""} 
            onClick={() => setFilter("high")}
          >
            Alto
          </button>
          <button 
            className={filter === "medium" ? "active" : ""} 
            onClick={() => setFilter("medium")}
          >
            Medio
          </button>
          <button 
            className={filter === "low" ? "active" : ""} 
            onClick={() => setFilter("low")}
          >
            Bajo
          </button>
        </div>
      </div>

      {/* =====================================================================
          TABLA DE RESERVAS
          ===================================================================== */}
      <div className="reservations-table-container">
        <table className="reservations-table">
          <thead>
            <tr>
              <th>Huésped</th>
              <th>Llegada</th>
              <th>Noches</th>
              <th>Precio</th>
              <th>Riesgo</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
                        {filteredReservations.map((reservation) => (
              <tr key={reservation.id} onClick={() => setSelectedReservation(reservation)} style={{ cursor: "pointer" }}>
                {/* Huésped */}
                <td>
                  <div className="guest-info">
                    <div className="guest-avatar">
                      {reservation.guest.split(" ").map(n => n[0]).join("")}
                    </div>
                    <div>
                      <div className="guest-name">{reservation.guest}</div>
                      <div className="guest-email">{reservation.email}</div>
                    </div>
                  </div>
                </td>
                
                {/* Llegada */}
                <td>
                  <div className="arrival-date">{formatDate(reservation.arrival)}</div>
                  <div className="days-left">
                    {daysUntilArrival(reservation.arrival) <= 7 
                      ? `${daysUntilArrival(reservation.arrival)} días` 
                      : ""}
                  </div>
                </td>
                
                {/* Noches */}
                <td>{reservation.nights} noches</td>
                
                {/* Precio */}
                <td>{reservation.price} EUR</td>
                
                {/* Riesgo */}
                <td>
                  <span className={`risk-badge ${reservation.riskLevel}`}>
                    {reservation.riskPercent}% {reservation.riskLevel === "high" ? "ALTO" : reservation.riskLevel === "medium" ? "MEDIO" : "BAJO"}
                  </span>
                </td>
                
                {/* Acción */}
                <td>
                  <div className="action-buttons">
                    {reservation.riskLevel === "high" && (
                      <>
                        <button className="btn-email">Email</button>
                        <button className="btn-call">Llamar</button>
                      </>
                    )}
                    {reservation.riskLevel === "medium" && (
                      <button className="btn-upgrade">Upgrade</button>
                    )}
                    {reservation.riskLevel === "low" && (
                      <span className="no-action">Sin acción</span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
    </Fragment>
  );
}

export default ReservationsTable;