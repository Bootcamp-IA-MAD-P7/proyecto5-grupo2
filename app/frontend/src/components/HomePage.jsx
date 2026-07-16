import React from "react";
import { ArrowRight, Sparkles } from "lucide-react";
import "./HomePage.css";

function HomePage({
  canEvaluate,
  onOpenEvaluation,
  onOpenOperations
}) {
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

          </div>
        </div>
      </div>

    </section>
  );
}

export default HomePage;
