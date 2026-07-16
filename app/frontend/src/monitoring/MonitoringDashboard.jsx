import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowLeft,
  BrainCircuit,
  CheckCircle2,
  Clock3,
  Database,
  GitCompareArrows,
  Info,
  RefreshCw,
  Replace,
  Server,
  ShieldCheck,
  TriangleAlert
} from "lucide-react";
import EducationalFooter from "../components/EducationalFooter.jsx";
import { fetchMonitoringOverview } from "./monitoringService.js";

const DRIFT_LABELS = {
  stable: "Estable",
  warning: "En observación",
  drift_detected: "Drift detectado",
  insufficient_data: "Muestra insuficiente"
};

function formatDate(value) {
  if (!value) return "Sin datos";
  return new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function formatModelType(value) {
  if (!value) return "Sin respuesta";
  return value
    .replace("RandomForestClassifier", "Random Forest")
    .replace("LogisticRegression", "Regresión logística");
}

function formatDriftMessage(drift, currentRows, minimumRows) {
  if (drift?.status === "insufficient_data") {
    return `Se necesitan al menos ${minimumRows} predicciones; hay ${currentRows} disponibles.`;
  }
  return drift?.message || "Esperando el informe operativo.";
}

function driftTone(status) {
  if (status === "stable") return "success";
  if (status === "warning" || status === "moderate" || status === "insufficient_data") {
    return "warning";
  }
  if (status === "drift_detected" || status === "high") return "danger";
  return "neutral";
}

function formatF1(value) {
  return value == null ? "--" : value.toFixed(3).replace(".", ",");
}

function experimentModules(experiments) {
  if (!experiments) return [];

  const neural = experiments.neural_network;
  const ab = experiments.ab_testing;
  const promotion = experiments.conditional_promotion;

  return [
    {
      key: "neural",
      icon: BrainCircuit,
      title: "Red neuronal",
      status: neural.decision === "retain_champion" ? "Experimento completado" : "Candidata válida",
      detail: `F1 validación ${formatF1(neural.validation_f1)} · gap ${formatF1(neural.overfitting_gap)}`
    },
    {
      key: "ab",
      icon: GitCompareArrows,
      title: "Comparación A/B",
      status: ab.decision === "retain_champion" ? "Champion retenido" : "Challenger superior",
      detail: `Champion ${formatF1(ab.champion_f1)} · Challenger ${formatF1(ab.challenger_f1)}`
    },
    {
      key: "promotion",
      icon: Replace,
      title: "Promoción condicionada",
      status: promotion.eligible ? "Promoción autorizada" : "Champion protegido",
      detail: promotion.eligible
        ? "Todas las reglas de promoción superadas"
        : `${promotion.failed_gates.length} reglas impiden el reemplazo`
    }
  ];
}

function StatusMark({ tone = "neutral", children }) {
  return <span className={`monitor-status monitor-status--${tone}`}>{children}</span>;
}

function Metric({ label, value, supporting, icon: Icon, tone = "neutral" }) {
  return (
    <article className={`monitor-metric monitor-metric--${tone}`}>
      <div className={`monitor-metric__icon monitor-metric__icon--${tone}`}>
        <Icon size={20} strokeWidth={1.8} aria-hidden="true" />
      </div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
        <span>{supporting}</span>
      </div>
    </article>
  );
}

function FeatureBars({ features, thresholds }) {
  if (!features?.length) {
    return (
      <div className="monitor-empty">
        <Clock3 size={24} strokeWidth={1.6} aria-hidden="true" />
        <div>
          <strong>Aún no hay una muestra concluyente</strong>
          <p>Las variables aparecerán aquí cuando el monitor alcance el mínimo operativo.</p>
        </div>
      </div>
    );
  }

  const high = thresholds?.high || 0.25;
  const scaleMax = Math.max(high * 1.35, ...features.map((feature) => feature.psi));

  return (
    <div className="monitor-bars">
      {features
        .slice()
        .sort((a, b) => b.psi - a.psi)
        .map((feature) => {
          const width = Math.min((feature.psi / scaleMax) * 100, 100);
          return (
            <div className="monitor-bar" key={feature.feature}>
              <div className="monitor-bar__label">
                <span>{feature.feature}</span>
                <strong>{feature.psi.toFixed(3)}</strong>
              </div>
              <div className="monitor-bar__track">
                <span
                  className={`monitor-bar__fill monitor-bar__fill--${driftTone(feature.status)}`}
                  style={{ width: `${width}%` }}
                />
              </div>
            </div>
          );
        })}
    </div>
  );
}

function MonitoringDashboard() {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updatedAt, setUpdatedAt] = useState(null);

  const loadOverview = useCallback(async () => {
    setLoading(true);
    const result = await fetchMonitoringOverview();
    setOverview(result);
    setUpdatedAt(new Date());
    setLoading(false);
  }, []);

  useEffect(() => {
    loadOverview();
    const intervalId = window.setInterval(loadOverview, 60000);
    return () => window.clearInterval(intervalId);
  }, [loadOverview]);

  const readiness = overview?.readiness?.data;
  const model = overview?.model?.data;
  const drift = overview?.drift?.data;
  const feedback = overview?.feedback?.data;
  const experiments = overview?.experiments?.data;
  const modules = experimentModules(experiments);
  const errors = useMemo(
    () =>
      Object.entries(overview || {})
        .filter(([, result]) => result.error)
        .map(([name, result]) => `${name}: ${result.error}`),
    [overview]
  );

  const currentRows = drift?.current_rows || 0;
  const minimumRows = drift?.minimum_current_rows || 100;
  const progress = Math.min((currentRows / minimumRows) * 100, 100);
  const driftStatus = drift?.status || "unknown";
  const systemReady = readiness?.status === "ready";

  return (
    <div className="monitor-page">
      <header className="monitor-header">
        <div className="monitor-header__inner">
          <a className="monitor-brand" href="/" aria-label="Volver al inicio de Hotel Insights">
            <img className="monitor-brand__mark" src="/logo.png" alt="" />
            <div>
              <strong>Hotel Insights</strong>
            </div>
          </a>
          <div className="monitor-header__context" aria-current="page">
            <Activity size={18} aria-hidden="true" />
            Monitorización
          </div>
          <div className="monitor-header__actions">
            <span className="monitor-updated">
              Actualizado {updatedAt ? formatDate(updatedAt) : "ahora"}
            </span>
            <a className="monitor-back-link" href="/">
              <ArrowLeft size={17} aria-hidden="true" />
              <span className="monitor-back-label monitor-back-label--long">Volver a la aplicación</span>
              <span className="monitor-back-label monitor-back-label--short">Volver a la app</span>
            </a>
            <button type="button" onClick={loadOverview} disabled={loading} title="Actualizar datos">
              <RefreshCw size={18} className={loading ? "is-spinning" : ""} aria-hidden="true" />
              <span>Actualizar</span>
            </button>
          </div>
        </div>
      </header>

      <main className="monitor-content">
        <section className="monitor-intro">
          <div>
            <p className="monitor-eyebrow">ESTADO DEL SISTEMA</p>
            <h1>Monitorización del modelo</h1>
            <p className="monitor-intro__copy">
              Seguimiento técnico del servicio, la calidad de los datos y la evolución del modelo.
            </p>
          </div>
          <StatusMark tone={systemReady ? "success" : "danger"}>
            {systemReady ? "Servicios disponibles" : "Revisión necesaria"}
          </StatusMark>
        </section>

        {errors.length > 0 && (
          <section className="monitor-alert" role="alert">
            <TriangleAlert size={20} aria-hidden="true" />
            <div>
              <strong>Algunas fuentes no respondieron</strong>
              <p>{errors.join(" | ")}</p>
            </div>
          </section>
        )}

      <section className="monitor-metrics" aria-label="Resumen operativo">
        <Metric
          label="Disponibilidad"
          value={systemReady ? "Operativa" : "No disponible"}
          supporting={readiness?.storage ? `Datos en ${readiness.storage}` : "Esperando respuesta"}
          icon={Server}
          tone={systemReady ? "success" : "danger"}
        />
        <Metric
          label="Modelo en servicio"
          value={formatModelType(model?.model_type)}
          supporting={model?.model_version || "Versión no disponible"}
          icon={ShieldCheck}
          tone="teal"
        />
        <Metric
          label="Predicciones reales para drift"
          value={`${currentRows} / ${minimumRows}`}
          supporting={currentRows >= minimumRows ? "Muestra suficiente" : "Sin incluir la cola histórica"}
          icon={Activity}
          tone={currentRows >= minimumRows ? "success" : "warning"}
        />
        <Metric
          label="Aprendizaje registrado"
          value={feedback?.total_records ?? "--"}
          supporting={feedback?.storage ? `Persistencia ${feedback.storage}` : "Sin respuesta"}
          icon={Database}
          tone="coral"
        />
      </section>

      <section className="monitor-section monitor-drift">
        <div className="monitor-section__heading">
          <div>
            <p className="monitor-eyebrow">DISTRIBUCIÓN DE ENTRADA</p>
            <h2>Data Drift</h2>
          </div>
          <StatusMark tone={driftTone(driftStatus)}>
            {DRIFT_LABELS[driftStatus] || "Sin respuesta"}
          </StatusMark>
        </div>

        <div className="monitor-drift__layout">
          <div className="monitor-drift__summary">
            <span>PSI máximo</span>
            <strong>{drift?.max_psi == null ? "--" : drift.max_psi.toFixed(3)}</strong>
            <p>{formatDriftMessage(drift, currentRows, minimumRows)}</p>
            <div className="monitor-progress" aria-label={`Muestra ${currentRows} de ${minimumRows}`}>
              <span style={{ width: `${progress}%` }} />
            </div>
            <small>{Math.round(progress)}% de la muestra mínima</small>
          </div>

          <div className="monitor-drift__features">
            <div className="monitor-thresholds">
              <span><i className="threshold-dot threshold-dot--stable" />Estable &lt; 0,10</span>
              <span><i className="threshold-dot threshold-dot--warning" />Aviso 0,10-0,25</span>
              <span><i className="threshold-dot threshold-dot--danger" />Drift &gt;= 0,25</span>
            </div>
            <FeatureBars features={drift?.features} thresholds={drift?.thresholds} />
            <div className="monitor-drift__notice">
              <Info size={18} aria-hidden="true" />
              <p>
                Solo se cuentan predicciones operativas nuevas. La cola histórica y sus
                evaluaciones automáticas se excluyen para no distorsionar el análisis.
              </p>
            </div>
          </div>
        </div>

        <dl className="monitor-details">
          <div><dt>Perfil</dt><dd>{drift?.profile_version || "--"}</dd></div>
          <div><dt>Fuente</dt><dd>{drift?.data_source || "--"}</dd></div>
          <div><dt>Límite</dt><dd>{drift?.sample_limit || "--"}</dd></div>
          <div><dt>Generado</dt><dd>{formatDate(drift?.generated_at)}</dd></div>
        </dl>
      </section>

      <section className="monitor-section">
        <div className="monitor-section__heading">
          <div>
            <p className="monitor-eyebrow">NIVEL EXPERTO</p>
            <h2>Ciclo de evolución del modelo</h2>
          </div>
          <span className="monitor-section__note">Sin datos simulados</span>
        </div>

        <div className="monitor-modules">
          <article className="monitor-module monitor-module--active">
            <div className="monitor-module__icon"><Activity size={21} aria-hidden="true" /></div>
            <div>
              <span>Data Drift</span>
              <strong>Operativo</strong>
              <p>PSI versionado y conectado a predicciones auditadas</p>
            </div>
            <CheckCircle2 size={20} className="monitor-module__check" aria-hidden="true" />
          </article>

          {modules.map(({ key, icon: Icon, title, status, detail }) => (
            <article className="monitor-module monitor-module--active" key={key}>
              <div className="monitor-module__icon"><Icon size={21} aria-hidden="true" /></div>
              <div>
                <span>{title}</span>
                <strong>{status}</strong>
                <p>{detail}</p>
              </div>
              <CheckCircle2 size={20} className="monitor-module__check" aria-hidden="true" />
            </article>
          ))}
        </div>
      </section>

        <aside className="monitor-operational-note" aria-label="Notas de monitorización">
          <span><RefreshCw size={15} aria-hidden="true" /> Actualización automática cada 60 segundos</span>
          <span><ShieldCheck size={15} aria-hidden="true" /> Las alertas de drift no reemplazan el modelo automáticamente</span>
        </aside>
      </main>

      <EducationalFooter />
    </div>
  );
}

export default MonitoringDashboard;
