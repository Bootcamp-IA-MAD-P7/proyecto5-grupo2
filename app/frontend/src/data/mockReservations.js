// Temporary demo fixtures. Replace with backend data when reservation endpoints exist.
export const mockReservations = [
  {
    id: "RES-2026-0847",
    guest: "María García",
    email: "m.garcia@email.com",
    arrival: "2026-07-15",
    nights: 3,
    price: 450,
    riskLevel: "high",
    riskPercent: 82,
    daysLeft: 3,
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
    daysLeft: 8,
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

export const mockAlerts = mockReservations
  .filter((reservation) => reservation.riskLevel === "high")
  .map((reservation) => ({
    ...reservation,
    daysLeft: reservation.daysLeft ?? daysUntilArrival(reservation.arrival)
  }));

function daysUntilArrival(dateString) {
  const arrival = new Date(dateString);
  const today = new Date();
  const diffTime = arrival - today;
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}
