import React, { useMemo, useState } from "react";
import Login from "./pages/Login";
import ReservationsTable from "./components/ReservationsTable";
import AlertsPanel from "./components/AlertsPanel";
import {
  ArrowUpRight,
  BellRing,
  CalendarDays,
  Check,
  ChevronDown,
  CircleDollarSign,
  Leaf,
  Menu,
  MessageSquareHeart,
  Moon,
  Palette,
  Play,
  Send,
  ShieldCheck,
  Sparkles,
  Waves
} from "lucide-react";
import { predictReservation } from "./services/predictionService";

const initialForm = {
  lead_time: 120,
  arrival_year: 2018,
  arrival_month: 7,
  arrival_date: 15,
  no_of_special_requests: 0,
  avg_price_per_room: 156,
  market_segment_type: "Online",
  no_of_weekend_nights: 1,
  no_of_week_nights: 2,
  type_of_meal_plan: "Meal Plan 1",
  room_type_reserved: "Room_Type 1",
  no_of_adults: 2,
  no_of_children: 0,
  required_car_parking_space: 0,
  repeated_guest: 0,
  no_of_previous_cancellations: 0,
  no_of_previous_bookings_not_canceled: 0
};

const scenarios = [
  {
    title: "Escapada urbana",
    description: "Reserva corta, canal online y precio alto.",
    meta: "2 noches · Online · 210 EUR",
    palette: ["#7d3941", "#c9a35d", "#fff7e9"],
    image:
      "https://images.unsplash.com/photo-1618220179428-22790b461013?auto=format&fit=crop&w=900&q=82",
    values: {
      lead_time: 42,
      arrival_year: 2018,
      arrival_month: 8,
      arrival_date: 12,
      avg_price_per_room: 210,
      market_segment_type: "Online",
      no_of_weekend_nights: 1,
      no_of_week_nights: 1,
      no_of_special_requests: 0,
      repeated_guest: 0
    }
  },
  {
    title: "Retiro wellness",
    description: "Más noches, solicitudes especiales y menor fricción.",
    meta: "5 noches · Offline · 148 EUR",
    palette: ["#0d6b5f", "#6f8d62", "#d9b56f"],
    image:
      "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=900&q=82",
    values: {
      lead_time: 28,
      arrival_year: 2018,
      arrival_month: 9,
      arrival_date: 6,
      avg_price_per_room: 148,
      market_segment_type: "Offline",
      no_of_weekend_nights: 2,
      no_of_week_nights: 3,
      no_of_special_requests: 2,
      repeated_guest: 1
    }
  },
  {
    title: "Suite flexible",
    description: "Lead time alto y señales a confirmar.",
    meta: "5 noches · Online · 186 EUR",
    palette: ["#b65f3f", "#415844", "#f4ead8"],
    image:
      "https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=900&q=82",
    values: {
      lead_time: 168,
      arrival_year: 2018,
      arrival_month: 12,
      arrival_date: 22,
      avg_price_per_room: 186,
      market_segment_type: "Online",
      no_of_weekend_nights: 1,
      no_of_week_nights: 4,
      no_of_special_requests: 0,
      repeated_guest: 0
    }
  }
];

const inputGroups = [
  {
    title: "Estancia",
    icon: CalendarDays,
    fields: [
      { name: "lead_time", label: "Antelación", type: "number", suffix: "días" },
      { name: "arrival_month", label: "Mes de llegada", type: "number" },
      { name: "arrival_date", label: "Día de llegada", type: "number" },
      { name: "no_of_weekend_nights", label: "Noches fin de semana", type: "number" },
      { name: "no_of_week_nights", label: "Noches entre semana", type: "number" }
    ]
  },
  {
    title: "Huésped",
    icon: MessageSquareHeart,
    fields: [
      { name: "no_of_adults", label: "Adultos", type: "number" },
      { name: "no_of_children", label: "Niños", type: "number" },
      { name: "no_of_special_requests", label: "Solicitudes especiales", type: "number" }
    ]
  },
  {
    title: "Reserva",
    icon: CircleDollarSign,
    fields: [
      { name: "avg_price_per_room", label: "Precio medio", type: "number", suffix: "EUR" },
      {
        name: "market_segment_type",
        label: "Canal",
        type: "select",
        options: ["Online", "Offline", "Corporate", "Complementary", "Aviation"]
      },
      {
        name: "room_type_reserved",
        label: "Habitación",
        type: "select",
        options: ["Room_Type 1", "Room_Type 2", "Room_Type 3", "Room_Type 4", "Room_Type 5"]
      }
    ]
  }
];

function App() {
  // Estado para controlar si mostrar login o la app
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  // Estado para controlar qué sección está activa
  const [activeSection, setActiveSection] = useState("reservas");

  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const stayNights = useMemo(
    () => Number(form.no_of_weekend_nights) + Number(form.no_of_week_nights),
    [form.no_of_weekend_nights, form.no_of_week_nights]
  );

  const probability = result ? Math.round(result.probability * 100) : 0;

  const operationalMetrics = useMemo(() => {
    const baseRisk = result ? probability : Math.round(Math.min(Number(form.lead_time) / 2.6, 78));
    const reviews = Math.max(6, Math.round(baseRisk / 3));
    const protectedRevenue = Math.round((Number(form.avg_price_per_room) * stayNights * reviews) / 100) / 10;
    const actions = result ? Math.max(1, Math.round(probability / 14)) : 3;

    return {
      reviews,
      protectedRevenue: `${protectedRevenue.toFixed(1)}k`,
      actions
    };
  }, [form.avg_price_per_room, form.lead_time, probability, result, stayNights]);

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function applyScenario(values) {
    setForm((current) => ({ ...current, ...values }));
    setResult(null);
    document.getElementById("predictor")?.scrollIntoView({ behavior: "smooth" });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setIsLoading(true);
    try {
      const prediction = await predictReservation(form);
      setResult(prediction);
    } finally {
      setIsLoading(false);
    }
  }

  // Si NO está logueado, muestra el Login
  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  // Si está logueado, muestra la app con navegación por secciones
  return (
    <main className="app-shell">
      <nav className={`topbar ${isMenuOpen ? "is-open" : ""}`} aria-label="Navegación principal">
                <a className="brand" href="#top" aria-label="Hotel Insights" style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <img src="/logo.png" alt="Hotel Insights" style={{ width: "40px", height: "40px", borderRadius: "8px", objectFit: "contain", background: "#fff", padding: "4px" }} />
          <span className="brand-copy">
            <strong>Hotel Insights</strong>
            <small>Guest risk studio</small>
          </span>
        </a>
        <div className="nav-links">
          <button 
            className={activeSection === "reservas" ? "active" : ""}
            onClick={() => setActiveSection("reservas")}
          >
            Reservas
          </button>
          <button 
            className={activeSection === "analisis" ? "active" : ""}
            onClick={() => setActiveSection("analisis")}
          >
            Análisis
          </button>
          <button 
            className={activeSection === "alertas" ? "active" : ""}
            onClick={() => setActiveSection("alertas")}
          >
            Alertas
          </button>
        </div>
        <button
          className="icon-button"
          aria-label="Abrir menú"
          aria-expanded={isMenuOpen}
          onClick={() => setIsMenuOpen((current) => !current)}
        >
          <Menu size={23} />
        </button>
      </nav>

      {/* SECCIÓN RESERVAS */}
      {activeSection === "reservas" && <ReservationsTable />}

      {/* SECCIÓN ANÁLISIS - Tu app actual exactamente igual */}
      {activeSection === "analisis" && (
        <>
          <section id="top" className="hero">
            <video
              className="hero-video"
              autoPlay
              muted
              loop
              playsInline
              poster="https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1800&q=84"
            >
              <source
                src="https://videos.pexels.com/video-files/3115406/3115406-uhd_2560_1440_25fps.mp4"
                type="video/mp4"
              />
            </video>
            <div className="hero-overlay" />
            <div className="hero-inner">
              <div className="hero-content">
                <div className="hero-kicker">
                  <Sparkles size={16} />
                  Boutique revenue desk
                </div>
                <h1>Reservas más claras antes de cada llegada.</h1>
                <p>
                  Hotel Insights reúne señales de reserva, riesgo y próxima acción
                  en una pantalla pensada para equipos de hotel que necesitan
                  decidir con calma, criterio y rapidez.
                </p>
                <div className="hero-actions">
                  <a className="primary-action" href="#predictor">
                    Probar reserva
                    <ArrowUpRight size={18} />
                  </a>
                  <a className="secondary-action" href="#portfolio">
                    Elegir escenario
                  </a>
                </div>
              </div>

              <aside className="hero-panel" aria-label="Resumen de hoy">
                <div className="hero-panel-head">
                  <span className="panel-label">Todas</span>
                  <strong>{operationalMetrics.reviews}</strong>
                </div>
                <p>reservas necesitan revisión antes del cierre.</p>
                <div className="panel-grid">
                  <span>Ingresos en juego</span>
                  <strong>{operationalMetrics.protectedRevenue}</strong>
                  <span>Contactos sugeridos</span>
                  <strong>{operationalMetrics.actions}</strong>
                </div>
              </aside>
            </div>
          </section>

          <section id="portfolio" className="experience-band">
            <div className="section-heading">
              <span>Escenarios</span>
              <h2>Prueba el riesgo desde estancias reales.</h2>
            </div>
            <div className="experience-grid">
              <article className="film-card">
                <video autoPlay muted loop playsInline>
                  <source
                    src="https://videos.pexels.com/video-files/853874/853874-hd_1920_1080_25fps.mp4"
                    type="video/mp4"
                  />
                </video>
                <div>
                  <span>
                    <Play size={16} />
                    Pulso de estancia
                  </span>
                  <p>
                    Usa los escenarios de la derecha para cambiar el formulario y
                    comprobar cómo se mueve el riesgo.
                  </p>
                </div>
              </article>

              <div className="scenario-list" aria-label="Escenarios de reserva">
                {scenarios.map((item) => (
                  <button
                    className="scenario-card"
                    key={item.title}
                    type="button"
                    onClick={() => applyScenario(item.values)}
                  >
                    <img src={item.image} alt="" />
                    <span className="scenario-copy">
                      <strong>{item.title}</strong>
                      <small>{item.description}</small>
                      <em>{item.meta}</em>
                    </span>
                    <span className="swatches" aria-label="Paleta visual">
                      {item.palette.map((color) => (
                        <i key={color} style={{ background: color }} />
                      ))}
                    </span>
                    <ArrowUpRight size={18} />
                  </button>
                ))}
              </div>
            </div>
          </section>

          <section id="predictor" className="predictor-layout">
            <div className="predictor-copy">
              <span className="eyebrow">Live prediction</span>
              <h2>Comprueba una reserva en menos de un minuto.</h2>
              <p>
                Ajusta los datos principales y obtén una lectura accionable: nivel
                de riesgo, señales principales y recomendación operativa.
              </p>
              <div className="signal-list">
                <span>
                  <Leaf size={18} />
                  Contexto de canal
                </span>
                <span>
                  <Moon size={18} />
                  Duración de estancia
                </span>
                <span>
                  <ShieldCheck size={18} />
                  Historial del huésped
                </span>
                <span>
                  <Palette size={18} />
                  Escenarios aplicables
                </span>
              </div>
            </div>

            <form className="reservation-form" onSubmit={handleSubmit}>
              {inputGroups.map((group) => {
                const Icon = group.icon;
                return (
                  <fieldset key={group.title}>
                    <legend>
                      <Icon size={18} />
                      {group.title}
                    </legend>
                    <div className="field-grid">
                      {group.fields.map((field) => (
                        <label key={field.name} className="field">
                          <span>{field.label}</span>
                          {field.type === "select" ? (
                            <span className="select-wrap">
                              <select
                                value={form[field.name]}
                                onChange={(event) => updateField(field.name, event.target.value)}
                              >
                                {field.options.map((option) => (
                                  <option key={option} value={option}>
                                    {option}
                                  </option>
                                ))}
                              </select>
                              <ChevronDown size={16} />
                            </span>
                          ) : (
                            <span className="input-wrap">
                              <input
                                min="0"
                                type={field.type}
                                value={form[field.name]}
                                onChange={(event) => updateField(field.name, event.target.value)}
                              />
                              {field.suffix && <em>{field.suffix}</em>}
                            </span>
                          )}
                        </label>
                      ))}
                    </div>
                  </fieldset>
                );
              })}

              <div className="toggle-row">
                <label>
                  <input
                    type="checkbox"
                    checked={Boolean(Number(form.repeated_guest))}
                    onChange={(event) => updateField("repeated_guest", event.target.checked ? 1 : 0)}
                  />
                  Huésped repetidor
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={Boolean(Number(form.required_car_parking_space))}
                    onChange={(event) =>
                      updateField("required_car_parking_space", event.target.checked ? 1 : 0)
                    }
                  />
                  Parking requerido
                </label>
              </div>

              <button className="submit-button" type="submit" disabled={isLoading}>
                {isLoading ? "Analizando reserva..." : "Calcular riesgo"}
                <Send size={18} />
              </button>
            </form>

            <aside className={`result-card ${result?.risk_level || "empty"}`}>
              <div className="result-top">
                <span>Riesgo estimado</span>
                <BellRing size={20} />
              </div>
              <div className="probability-ring" style={{ "--value": `${probability}%` }}>
                <strong>{result ? `${probability}%` : "--"}</strong>
                <span>{result ? result.risk_label : "Pendiente"}</span>
              </div>
              <div className="result-summary">
                <p>
                  {result
                    ? result.prediction === "Canceled"
                      ? "La reserva muestra señales de posible cancelación."
                      : "La reserva parece estable, con baja fricción operativa."
                    : `Configura una estancia de ${stayNights} noches y calcula el riesgo.`}
                </p>
              </div>
              {result && (
                <>
                  <ul className="factor-list">
                    {result.main_factors.map((factor) => (
                      <li key={factor}>
                        <Check size={16} />
                        {factor}
                      </li>
                    ))}
                  </ul>
                  <div className="recommendation">
                    <Waves size={18} />
                    <p>{result.recommendation}</p>
                  </div>
                </>
              )}
            </aside>
          </section>

          <section id="signals" className="signals-section">
            <div>
              <span className="eyebrow">Operational signals</span>
              <h2>Un plan sencillo después de cada predicción.</h2>
            </div>
            <div className="metric-row">
              <article>
                <span>Reservas a revisar</span>
                <strong>{operationalMetrics.reviews}</strong>
                <small>Prioridad de hoy</small>
              </article>
              <article>
                <span>Ingresos protegidos</span>
                <strong>{operationalMetrics.protectedRevenue}</strong>
                <small>Estimación semanal</small>
              </article>
              <article>
                <span>Acciones sugeridas</span>
                <strong>{operationalMetrics.actions}</strong>
                <small>Contactos proactivos</small>
              </article>
            </div>
          </section>
        </>
      )}

      {/* SECCIÓN ALERTAS */}
      {activeSection === "alertas" && <AlertsPanel />}
    </main>
  );
}

     


export default App;