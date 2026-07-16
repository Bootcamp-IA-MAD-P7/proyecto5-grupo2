import React from "react";
import {
  BarChart3,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  Database,
  ExternalLink,
  Layers3,
  ShieldAlert,
  SplitSquareVertical
} from "lucide-react";
import "./ModelPage.css";

const featureGroups = [
  {
    title: "Reserva y estancia",
    features: ["Antelación", "Fecha de llegada", "Noches de semana", "Noches de fin de semana"]
  },
  {
    title: "Perfil e historial",
    features: ["Adultos y niños", "Huésped repetidor", "Cancelaciones previas", "Reservas completadas"]
  },
  {
    title: "Producto y canal",
    features: ["Precio medio", "Solicitudes especiales", "Habitación", "Plan de comidas", "Segmento"]
  }
];

const importanceRows = [
  { label: "Antelación de la reserva", value: 34.12 },
  { label: "Solicitudes especiales", value: 16.69 },
  { label: "Precio medio por habitación", value: 11.46 },
  { label: "Mes de llegada", value: 7.29 },
  { label: "Canal online", value: 4.62 }
];

const testMetrics = [
  { label: "Accuracy", value: "88,55 %" },
  { label: "Precisión cancelación", value: "82,33 %" },
  { label: "Recall cancelación", value: "82,84 %" },
  { label: "F1 cancelación", value: "82,58 %", featured: true },
  { label: "ROC-AUC", value: "94,99 %" }
];

function ModelPage({ modelInfo }) {
  const modelReady = Boolean(modelInfo?.model_loaded);

  return (
    <section className="model-page" aria-labelledby="model-page-title">
      <header className="model-page-hero">
        <div>
          <span className="model-page-kicker"><BookOpen size={17} /> Documentación educativa</span>
          <h1 id="model-page-title">Modelo y proceso analítico</h1>
          <p>
            Una lectura separada del producto para explicar cómo se prepararon los datos,
            qué aprendimos en el EDA y por qué se seleccionó el modelo desplegado.
          </p>
        </div>
        <div className="model-hero-actions">
          <span className={`model-artifact-status ${modelReady ? "ready" : "unavailable"}`}>
            <BrainCircuit size={18} />
            {modelReady ? "Modelo desplegado y cargado" : "Modelo no disponible"}
          </span>
          <a href="/monitoring.html" target="_blank" rel="noreferrer">
            Ver monitorización MLOps <ExternalLink size={16} />
          </a>
        </div>
      </header>

      <div className="model-summary-grid" aria-label="Resumen del dataset">
        <article><Database size={21} /><span>Reservas históricas</span><strong>36.275</strong></article>
        <article><Layers3 size={21} /><span>Variables predictoras</span><strong>17</strong><small>14 numéricas · 3 categóricas</small></article>
        <article><BarChart3 size={21} /><span>Clase cancelada</span><strong>32,76 %</strong><small>11.885 reservas</small></article>
        <article><CheckCircle2 size={21} /><span>Valores ausentes</span><strong>0</strong><small>en el CSV de trabajo</small></article>
      </div>

      <section className="model-content-section" aria-labelledby="dataset-title">
        <div className="model-section-heading">
          <span>01 · Datos</span>
          <h2 id="dataset-title">Composición del dataset</h2>
          <p>El identificador de reserva se conserva para trazabilidad, pero no entra en el modelo.</p>
        </div>

        <div className="dataset-layout">
          <article className="target-card">
            <h3>Variable objetivo · booking_status</h3>
            <div className="target-bar" aria-label="67,24 % no canceladas y 32,76 % canceladas">
              <span className="not-canceled" style={{ width: "67.24%" }}>67,24 %</span>
              <span className="canceled" style={{ width: "32.76%" }}>32,76 %</span>
            </div>
            <div className="target-legend">
              <span><i className="not-canceled" /> 24.390 no canceladas</span>
              <span><i className="canceled" /> 11.885 canceladas</span>
            </div>
          </article>

          <div className="feature-group-grid">
            {featureGroups.map((group) => (
              <article key={group.title}>
                <h3>{group.title}</h3>
                <ul>
                  {group.features.map((feature) => <li key={feature}>{feature}</li>)}
                </ul>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="model-content-section eda-section" aria-labelledby="eda-title">
        <div className="model-section-heading">
          <span>02 · EDA</span>
          <h2 id="eda-title">Señales observadas en los datos</h2>
          <p>Patrones descriptivos que orientaron el modelado; asociación no significa causalidad.</p>
        </div>

        <div className="eda-grid">
          <article>
            <span>Antelación mediana</span>
            <strong>122 días</strong>
            <p>en reservas canceladas, frente a <b>39 días</b> en no canceladas.</p>
          </article>
          <article>
            <span>Sin solicitudes especiales</span>
            <strong>43,21 %</strong>
            <p>de cancelación, frente a <b>20,24 %</b> cuando existe al menos una.</p>
          </article>
          <article>
            <span>Segmento online</span>
            <strong>36,51 %</strong>
            <p>de cancelación histórica, frente a <b>10,91 %</b> en Corporate.</p>
          </article>
        </div>
      </section>

      <section className="model-content-section" aria-labelledby="process-title">
        <div className="model-section-heading">
          <span>03 · Entrenamiento</span>
          <h2 id="process-title">Del baseline al modelo desplegado</h2>
          <p>El test se mantuvo aislado hasta congelar la selección y los criterios de aceptación.</p>
        </div>

        <ol className="training-timeline">
          <li><span>1</span><div><strong>Split estratificado</strong><p>70 % train · 15 % validación · 15 % test, con random_state 42.</p></div></li>
          <li><span>2</span><div><strong>Preprocesamiento reproducible</strong><p>One-Hot Encoding para categóricas y contrato fijo de 17 variables.</p></div></li>
          <li><span>3</span><div><strong>Baseline interpretable</strong><p>Regresión logística balanceada: F1 de validación 68,70 %.</p></div></li>
          <li><span>4</span><div><strong>Selección del Random Forest</strong><p>200 árboles, profundidad 18 y F1 de validación 81,05 %.</p></div></li>
          <li><span>5</span><div><strong>Holdout final</strong><p>5.442 filas abiertas una sola vez: F1 82,58 % y criterios superados.</p></div></li>
        </ol>

        <div className="model-comparison-card">
          <h3>Mejora sobre el baseline · F1 validación</h3>
          <div><span>Logistic Regression</span><i><b style={{ width: "68.7%" }} /></i><strong>68,70 %</strong></div>
          <div><span>Random Forest</span><i><b className="champion" style={{ width: "81.05%" }} /></i><strong>81,05 %</strong></div>
        </div>
      </section>

      <section className="model-content-section" aria-labelledby="results-title">
        <div className="model-section-heading">
          <span>04 · Evaluación</span>
          <h2 id="results-title">Resultados sobre test reservado</h2>
          <p>Clase positiva: Canceled · evaluación final del 15 de julio de 2026.</p>
        </div>

        <div className="test-metrics-grid">
          {testMetrics.map((metric) => (
            <article className={metric.featured ? "featured" : ""} key={metric.label}>
              <span>{metric.label}</span><strong>{metric.value}</strong>
            </article>
          ))}
        </div>

        <div className="importance-layout">
          <article className="importance-card">
            <h3>Importancia global de variables</h3>
            <p>Participación dentro del Random Forest; no representa efecto causal.</p>
            {importanceRows.map((feature) => (
              <div className="importance-row" key={feature.label}>
                <span>{feature.label}</span>
                <i><b style={{ width: `${(feature.value / 34.12) * 100}%` }} /></i>
                <strong>{feature.value.toFixed(2).replace(".", ",")} %</strong>
              </div>
            ))}
          </article>

          <article className="model-configuration-card">
            <h3><SplitSquareVertical size={18} /> Configuración seleccionada</h3>
            <dl>
              <div><dt>Familia</dt><dd>RandomForestClassifier</dd></div>
              <div><dt>Árboles</dt><dd>200</dd></div>
              <div><dt>Profundidad máxima</dt><dd>18</dd></div>
              <div><dt>Balanceo</dt><dd>balanced_subsample</dd></div>
              <div><dt>Versión</dt><dd>{modelInfo?.model_version || "random_forest_champion_v0.1.0"}</dd></div>
            </dl>
          </article>
        </div>
      </section>

      <section className="model-limitations" aria-labelledby="limitations-title">
        <ShieldAlert size={24} />
        <div>
          <h2 id="limitations-title">Cómo interpretar esta solución</h2>
          <ul>
            <li>El dataset recoge reservas de 2017–2018; el Data Drift debe vigilar cambios posteriores.</li>
            <li>Las explicaciones locales sirven para priorizar la revisión, no demuestran causalidad.</li>
            <li>El test quedó cerrado; futuros modelos necesitan datos nuevos o un protocolo independiente.</li>
            <li>Es un proyecto educativo de apoyo a decisiones y no automatiza decisiones sobre clientes.</li>
          </ul>
        </div>
      </section>
    </section>
  );
}

export default ModelPage;
