import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ClipboardCheck,
  Database,
  House,
  LayoutList,
  RefreshCw,
  ShieldCheck,
  Sparkles
} from "lucide-react";
import AlertsPanel from "./components/AlertsPanel";
import FeedbackHistory from "./components/FeedbackHistory";
import GuidedReservationFlow from "./components/GuidedReservationFlow";
import HomePage from "./components/HomePage";
import ReservationDetailModal from "./components/ReservationDetailModal";
import ReservationEvaluation from "./components/ReservationEvaluation";
import ReservationsTable from "./components/ReservationsTable";
import WorkflowSteps from "./components/WorkflowSteps";
import {
  applyPredictionToReservation,
  fetchFeedbackSummary,
  fetchModelInfo,
  fetchPredictedReservations
} from "./services/predictionService";

function App() {
  const [activeSection, setActiveSection] = useState("home");
  const [operationsView, setOperationsView] = useState("guided");
  const [reservations, setReservations] = useState([]);
  const [datasetMeta, setDatasetMeta] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [feedbackSummary, setFeedbackSummary] = useState(null);
  const [selectedReservation, setSelectedReservation] = useState(null);
  const [evaluationReservation, setEvaluationReservation] = useState(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [workspaceError, setWorkspaceError] = useState("");

  const loadWorkspace = useCallback(async () => {
    setIsLoading(true);
    setWorkspaceError("");

    const [reservationsResult, modelResult, feedbackResult] = await Promise.allSettled([
      fetchPredictedReservations(16),
      fetchModelInfo(),
      fetchFeedbackSummary()
    ]);

    const errors = [];

    if (reservationsResult.status === "fulfilled") {
      const data = reservationsResult.value;
      const orderedByRisk = [...data.reservations].sort((a, b) => b.riskPercent - a.riskPercent);
      const firstPriority = orderedByRisk[0] || null;
      setReservations(data.reservations);
      setDatasetMeta(data);
      setSelectedReservation((current) =>
        data.reservations.find((item) => item.id === current?.id) || firstPriority
      );
      setEvaluationReservation((current) =>
        data.reservations.find((item) => item.id === current?.id) || firstPriority
      );
    } else {
      errors.push("No se pudieron cargar y evaluar las reservas del backend.");
    }

    if (modelResult.status === "fulfilled") {
      setModelInfo(modelResult.value);
    } else {
      errors.push("No se pudo consultar el estado del Champion.");
    }

    if (feedbackResult.status === "fulfilled") {
      setFeedbackSummary(feedbackResult.value);
    } else {
      errors.push("No se pudo consultar el resumen de feedback.");
    }

    setWorkspaceError(errors.join(" "));
    setIsLoading(false);
  }, []);

  useEffect(() => {
    loadWorkspace();
  }, [loadWorkspace]);

  const riskCounts = useMemo(
    () =>
      reservations.reduce(
        (counts, reservation) => ({
          ...counts,
          [reservation.riskLevel]: counts[reservation.riskLevel] + 1
        }),
        { high: 0, medium: 0, low: 0 }
      ),
    [reservations]
  );

  const priorityOrder = useMemo(
    () => [...reservations].sort((a, b) => b.riskPercent - a.riskPercent),
    [reservations]
  );

  const nextPriorityReservation = useMemo(() => {
    if (!evaluationReservation || priorityOrder.length < 2) return null;
    const currentIndex = priorityOrder.findIndex((item) => item.id === evaluationReservation.id);
    return priorityOrder[currentIndex + 1] || priorityOrder[0] || null;
  }, [evaluationReservation, priorityOrder]);

  function openReservation(reservation) {
    setSelectedReservation(reservation);
    setIsDetailOpen(true);
  }

  function showSection(section) {
    setActiveSection(section);
    window.scrollTo({ top: 0, left: 0 });
  }

  function evaluateReservation(reservation) {
    setSelectedReservation(reservation);
    setEvaluationReservation(reservation);
    setIsDetailOpen(false);
    showSection("evaluation");
  }

  function handlePredictionComplete(inputData, prediction) {
    if (!evaluationReservation) return;

    const updatedReservation = applyPredictionToReservation(
      evaluationReservation,
      inputData,
      prediction
    );

    setReservations((current) =>
      current.map((reservation) =>
        reservation.id === updatedReservation.id ? updatedReservation : reservation
      )
    );
    setSelectedReservation(updatedReservation);
    setEvaluationReservation(updatedReservation);
  }

  async function refreshFeedbackSummary() {
    try {
      setFeedbackSummary(await fetchFeedbackSummary());
    } catch {
      setWorkspaceError("El feedback se guardó, pero no se pudo actualizar su contador.");
    }
  }

  const modelReady = Boolean(modelInfo?.model_loaded);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-inner">
          <button
            className="brand-button"
            type="button"
            onClick={() => showSection("home")}
            aria-label="Ir al inicio"
          >
            <img src="/logo.png" alt="" />
            <span>
              <strong>Hotel Insights</strong>
              <small>Control de cancelaciones</small>
            </span>
          </button>

          <nav className="primary-navigation" aria-label="Secciones principales">
            <button
              type="button"
              className={activeSection === "home" ? "active" : ""}
              onClick={() => showSection("home")}
            >
              <House size={18} />
              Inicio
            </button>
            <button
              type="button"
              className={activeSection === "operations" ? "active" : ""}
              onClick={() => showSection("operations")}
            >
              <LayoutList size={18} />
              Operación
            </button>
            <button
              type="button"
              className={activeSection === "evaluation" ? "active" : ""}
              onClick={() => showSection("evaluation")}
              disabled={!evaluationReservation}
            >
              <Sparkles size={18} />
              Evaluar reserva
            </button>
            <button
              type="button"
              className={activeSection === "feedback" ? "active" : ""}
              onClick={() => showSection("feedback")}
            >
              <ClipboardCheck size={18} />
              Feedback
            </button>
          </nav>

          <div className="system-status" aria-label="Estado del sistema">
            <span className={`status-badge ${modelReady ? "ready" : "unavailable"}`}>
              <ShieldCheck size={16} />
              {modelReady ? "Champion activo" : "Champion no disponible"}
            </span>
            <span className="status-badge" title={modelInfo?.model_version || "Versión no disponible"}>
              <Activity size={16} />
              {modelInfo?.model_version || "Sin versión"}
            </span>
          </div>
        </div>
      </header>

      <main className={`workspace-main ${activeSection === "home" ? "home-main" : ""}`}>
        {workspaceError && (
          <div className="workspace-alert" role="alert">
            <AlertTriangle size={18} />
            <span>{workspaceError}</span>
          </div>
        )}

        {activeSection === "home" ? (
          <HomePage
            canEvaluate={Boolean(evaluationReservation)}
            datasetMeta={datasetMeta}
            feedbackSummary={feedbackSummary}
            isLoading={isLoading}
            modelInfo={modelInfo}
            reservationsCount={reservations.length}
            onOpenOperations={() => showSection("operations")}
            onOpenEvaluation={() => showSection("evaluation")}
          />
        ) : activeSection === "operations" ? (
          <section className="operations-section" aria-labelledby="operations-title">
            <WorkflowSteps activeStep={1} completedThrough={0} />
            <div className="section-toolbar">
              <div>
                <span className="section-kicker">Operación diaria</span>
                <h1 id="operations-title">Reservas evaluadas por prioridad</h1>
                <p>
                  Muestra histórica evaluada con el modelo Champion activo.
                </p>
              </div>
              <div className="toolbar-actions">
                <div className="segmented-control" aria-label="Vista de reservas">
                  <button
                    type="button"
                    className={operationsView === "guided" ? "active" : ""}
                    onClick={() => setOperationsView("guided")}
                  >
                    Flujo guiado
                  </button>
                  <button
                    type="button"
                    className={operationsView === "all" ? "active" : ""}
                    onClick={() => setOperationsView("all")}
                  >
                    Todas
                  </button>
                  <button
                    type="button"
                    className={operationsView === "priority" ? "active" : ""}
                    onClick={() => setOperationsView("priority")}
                  >
                    Prioritarias
                  </button>
                </div>
                <button
                  className="icon-button"
                  type="button"
                  onClick={loadWorkspace}
                  disabled={isLoading}
                  aria-label="Actualizar datos"
                  title="Actualizar datos"
                >
                  <RefreshCw size={19} className={isLoading ? "spin" : ""} />
                </button>
              </div>
            </div>

            <div className="metric-grid" aria-label="Resumen de reservas cargadas">
              <article>
                <Database size={20} />
                <span>Analizadas</span>
                <strong>{isLoading ? "--" : reservations.length}</strong>
                <small>de {datasetMeta?.totalAvailable?.toLocaleString("es-ES") || "--"} disponibles</small>
              </article>
              <article className="metric-high">
                <AlertTriangle size={20} />
                <span>Riesgo alto</span>
                <strong>{isLoading ? "--" : riskCounts.high}</strong>
                <small>revisión prioritaria</small>
              </article>
              <article className="metric-medium">
                <Activity size={20} />
                <span>Riesgo medio</span>
                <strong>{isLoading ? "--" : riskCounts.medium}</strong>
                <small>seguimiento recomendado</small>
              </article>
              <article className="metric-low">
                <ShieldCheck size={20} />
                <span>Riesgo bajo</span>
                <strong>{isLoading ? "--" : riskCounts.low}</strong>
                <small>observación normal</small>
              </article>
            </div>

            {operationsView === "guided" ? (
              <GuidedReservationFlow
                reservations={reservations}
                selectedReservation={selectedReservation}
                isLoading={isLoading}
                onSelect={setSelectedReservation}
                onOpenDetail={openReservation}
                onEvaluate={evaluateReservation}
              />
            ) : operationsView === "all" ? (
              <ReservationsTable
                reservations={reservations}
                isLoading={isLoading}
                onSelect={openReservation}
                onEvaluate={evaluateReservation}
              />
            ) : (
              <AlertsPanel
                reservations={reservations}
                isLoading={isLoading}
                onSelect={openReservation}
                onEvaluate={evaluateReservation}
              />
            )}

            {datasetMeta?.source && (
              <p className="data-source">Fuente de datos: {datasetMeta.source}</p>
            )}
          </section>
        ) : activeSection === "feedback" ? (
          <FeedbackHistory onFeedbackChanged={refreshFeedbackSummary} />
        ) : (
          <ReservationEvaluation
            reservation={evaluationReservation}
            modelInfo={modelInfo}
            onBack={() => showSection("operations")}
            onPredictionComplete={handlePredictionComplete}
            onFeedbackSaved={refreshFeedbackSummary}
            onNextReservation={
              nextPriorityReservation ? () => evaluateReservation(nextPriorityReservation) : null
            }
          />
        )}
      </main>

      {isDetailOpen && selectedReservation && (
        <ReservationDetailModal
          reservation={selectedReservation}
          onClose={() => setIsDetailOpen(false)}
          onEvaluate={() => evaluateReservation(selectedReservation)}
        />
      )}
    </div>
  );
}

export default App;
