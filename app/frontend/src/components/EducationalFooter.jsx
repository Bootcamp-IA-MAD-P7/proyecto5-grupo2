import React from "react";
import { GraduationCap, ShieldCheck } from "lucide-react";
import "./EducationalFooter.css";

function EducationalFooter() {
  return (
    <footer className="educational-footer" aria-label="Información educativa del proyecto">
      <div className="educational-footer-inner">
        <section className="footer-identity">
          <div className="footer-brand-lockup">
            <img src="/logo.png" alt="" />
            <div>
              <strong>Hotel Insights</strong>
              <p>Sistema predictivo de riesgo de cancelación de reservas hoteleras.</p>
            </div>
          </div>
          <small>© 2026 · Proyecto educativo de clasificación y despliegue web.</small>
        </section>

        <section>
          <h2><GraduationCap size={16} /> Proyecto</h2>
          <p>Trabajo académico</p>
          <p>Grupo 2 · Bootcamp IA</p>
        </section>

        <section>
          <h2>Stack</h2>
          <p>React · Vite · FastAPI</p>
          <p>PostgreSQL · Docker · AWS</p>
        </section>

        <section>
          <h2><ShieldCheck size={16} /> Uso responsable</h2>
          <p>Apoyo a la priorización operativa</p>
          <p>No sustituye el criterio profesional</p>
        </section>
      </div>
    </footer>
  );
}

export default EducationalFooter;
