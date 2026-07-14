import React from "react";
import {
  ArrowRight,
  BarChart3,
  ClipboardCheck,
  Database,
  ShieldCheck,
  Sparkles
} from "lucide-react";
import "./HomePage.css";

function formatCount(value) {
  return typeof value === "number" ? value.toLocaleString("es-ES") : "--";
}

function HomePage({
  canEvaluate,
  datasetMeta,
  feedbackSummary,
  isLoading,
  modelInfo,
  reservationsCount,
  onOpenEvaluation,
  onOpenOperations
}) {
  const modelReady = Boolean(modelInfo?.model_loaded);
  const modelStatus = isLoading
    ? "Conectando con el modelo"
    : modelReady
      ? "Champion activo"
      : "Champion no disponible";

  return (
    <section className="home-page" aria-labelledby="home-title">
      <div className="home-hero">
        <img
          className="home-hero-image"
          src="/hotel-bg.jpg"
          alt="Piscina y terraza de un hotel frente al mar"
        />
        <div className="home-hero-overlay" />

        <div className="home-hero-inner">
          <div className="home-hero-copy">
            <span className="home-eyebrow">
              <Sparkles size={17} />
              Inteligencia operativa para hoteles
            </span>
            <h1 id="home-title">Hotel Insights</h1>
            <p>
              Anticipa cancelaciones, prioriza las reservas que necesitan atención y convierte
              cada predicción en una decisión clara para el equipo del hotel.
            </p>

            <div className="home-actions">
              <button className="home-primary-action" type="button" onClick={onOpenOperations}>
                Abrir operación
                <ArrowRight size={19} />
              </button>
              <button
                className="home-secondary-action"
                type="button"
                onClick={onOpenEvaluation}
                disabled={!canEvaluate}
              >
                <Sparkles size={18} />
                Evaluar una reserva
              </button>
            </div>

            <div className={`home-model-status ${modelReady ? "ready" : isLoading ? "loading" : "unavailable"}`}>
              <ShieldCheck size={18} />
              <span>{modelStatus}</span>
              {modelInfo?.model_version && <small>{modelInfo.model_version}</small>}
            </div>
          </div>
        </div>
      </div>

      <section className="home-live-band" aria-labelledby="home-live-title">
        <div className="home-live-inner">
          <div className="home-live-heading">
            <span>Datos conectados</span>
            <h2 id="home-live-title">Una lectura real para la operación.</h2>
          </div>

          <div className="home-live-metrics">
            <article>
              <Database size={22} />
              <span>Histórico disponible</span>
              <strong>{formatCount(datasetMeta?.totalAvailable)}</strong>
              <small>reservas en la fuente actual</small>
            </article>
            <article>
              <BarChart3 size={22} />
              <span>Muestra evaluada</span>
              <strong>{isLoading ? "--" : formatCount(reservationsCount)}</strong>
              <small>predicciones del Champion</small>
            </article>
            <article>
              <ClipboardCheck size={22} />
              <span>Seguimiento registrado</span>
              <strong>{formatCount(feedbackSummary?.total_records)}</strong>
              <small>resultados observados</small>
            </article>
          </div>
        </div>
      </section>
    </section>
  );
}

export default HomePage;
