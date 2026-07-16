import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  BrainCircuit,
  CheckCircle2,
  Clock3,
  Database,
  GitCompareArrows,
  RefreshCw,
  Replace,
  Server,
  ShieldCheck,
  TriangleAlert
} from "lucide-react";
import { fetchMonitoringOverview } from "./monitoringService.js";

const DRIFT_LABELS = {
  stable: "Estable",
  warning: "En observacion",
  drift_detected: "Drift detectado",
  insufficient_data: "Muestra insuficiente"
};

const MODULES = [
  {
    key: "neural",
    icon: BrainCircuit,
    title: "Red neuronal",
    status: "Pendiente de evaluacion",
    detail: "Sin experimento registrado"
  },
  {
    key: "ab",
    icon: GitCompareArrows,
    title: "Comparacion A/B",
    status: "Pendiente de evaluacion",
    detail: "Sin reparto de evaluacion definido"
  },
  {
    key: "promotion",
    icon: Replace,
    title: "Promocion condicionada",
    status: "Pendiente de evaluacion",
    detail: "El Champion no se reemplaza automaticamente"
  }
];

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
    .replace("LogisticRegression", "Regresion logistica");
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

function StatusMark({ tone = "neutral", children }) {
  return <span className={`monitor-status monitor-status--${tone}`}>{children}</span>;
}

function Metric({ label, value, supporting, icon: Icon, tone = "neutral" }) {
  return (
    <article className="monitor-metric">
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
          <strong>Aun no hay una muestra concluyente</strong>
          <p>Las variables apareceran aqui cuando el monitor alcance el minimo operativo.</p>
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
    <main className="monitor-page">
      <header className="monitor-header">
        <div className="monitor-header__inner">
          <div className="monitor-brand">
            <img className="monitor-brand__mark" src="/logo.png" alt="" />
            <div>
              <strong>Hotel Insights</strong>
              <span>Control operativo MLOps</span>
            </div>
          </div>
          <div className="monitor-header__actions">
            <span className="monitor-updated">
              Actualizado {updatedAt ? formatDate(updatedAt) : "ahora"}
            </span>
            <button type="button" onClick={loadOverview} disabled={loading} title="Actualizar datos">
              <RefreshCw size={18} className={loading ? "is-spinning" : ""} aria-hidden="true" />
              <span>Actualizar</span>
            </button>
          </div>
        </div>
      </header>

      <section className="monitor-intro">
        <div>
          <p className="monitor-eyebrow">ESTADO DEL SISTEMA</p>
          <h1>Monitorizacion del modelo</h1>
        </div>
        <StatusMark tone={systemReady ? "success" : "danger"}>
          {systemReady ? "Servicios disponibles" : "Revision necesaria"}
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
          supporting={model?.model_version || "Version no disponible"}
          icon={ShieldCheck}
          tone="teal"
        />
        <Metric
          label="Muestra de drift"
          value={`${currentRows} / ${minimumRows}`}
          supporting={currentRows >= minimumRows ? "Muestra suficiente" : "Predicciones operativas"}
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
            <p className="monitor-eyebrow">DISTRIBUCION DE ENTRADA</p>
            <h2>Data Drift</h2>
          </div>
          <StatusMark tone={driftTone(driftStatus)}>
            {DRIFT_LABELS[driftStatus] || "Sin respuesta"}
          </StatusMark>
        </div>

        <div className="monitor-drift__layout">
          <div className="monitor-drift__summary">
            <span>PSI maximo</span>
            <strong>{drift?.max_psi == null ? "--" : drift.max_psi.toFixed(3)}</strong>
            <p>{formatDriftMessage(drift, currentRows, minimumRows)}</p>
            <div className="monitor-progress" aria-label={`Muestra ${currentRows} de ${minimumRows}`}>
              <span style={{ width: `${progress}%` }} />
            </div>
            <small>{Math.round(progress)}% de la muestra minima</small>
          </div>

          <div className="monitor-drift__features">
            <div className="monitor-thresholds">
              <span><i className="threshold-dot threshold-dot--stable" />Estable &lt; 0,10</span>
              <span><i className="threshold-dot threshold-dot--warning" />Aviso 0,10-0,25</span>
              <span><i className="threshold-dot threshold-dot--danger" />Drift &gt;= 0,25</span>
            </div>
            <FeatureBars features={drift?.features} thresholds={drift?.thresholds} />
          </div>
        </div>

        <dl className="monitor-details">
          <div><dt>Perfil</dt><dd>{drift?.profile_version || "--"}</dd></div>
          <div><dt>Fuente</dt><dd>{drift?.data_source || "--"}</dd></div>
          <div><dt>Limite</dt><dd>{drift?.sample_limit || "--"}</dd></div>
          <div><dt>Generado</dt><dd>{formatDate(drift?.generated_at)}</dd></div>
        </dl>
      </section>

      <section className="monitor-section">
        <div className="monitor-section__heading">
          <div>
            <p className="monitor-eyebrow">NIVEL EXPERTO</p>
            <h2>Ciclo de evolucion del modelo</h2>
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

          {MODULES.map(({ key, icon: Icon, title, status, detail }) => (
            <article className="monitor-module" key={key}>
              <div className="monitor-module__icon"><Icon size={21} aria-hidden="true" /></div>
              <div>
                <span>{title}</span>
                <strong>{status}</strong>
                <p>{detail}</p>
              </div>
              <Clock3 size={20} className="monitor-module__pending" aria-hidden="true" />
            </article>
          ))}
        </div>
      </section>

      <footer className="monitor-footer">
        <span>Actualizacion automatica cada 60 segundos</span>
        <span>Las alertas de drift no sustituyen al Champion automaticamente</span>
      </footer>
    </main>
  );
}

export default MonitoringDashboard;
