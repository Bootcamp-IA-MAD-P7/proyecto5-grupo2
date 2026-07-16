import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  Database,
  House,
  LayoutList,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles
} from "lucide-react";
import AlertsPanel from "./components/AlertsPanel";
import EducationalFooter from "./components/EducationalFooter";
import FeedbackHistory from "./components/FeedbackHistory";
import GuidedReservationFlow from "./components/GuidedReservationFlow";
import HomePage from "./components/HomePage";
import ModelPage from "./components/ModelPage";
import ReservationDetailModal from "./components/ReservationDetailModal";
import ReservationEvaluation from "./components/ReservationEvaluation";
import ReservationsTable from "./components/ReservationsTable";
import WorkflowSteps from "./components/WorkflowSteps";
import {
  applyPredictionToReservation,
  fetchFeedbackSummary,
  fetchModelInfo,
  fetchPredictedReservationById,
  fetchPredictedReservations
} from "./services/predictionService";

const RESERVATIONS_PAGE_SIZE = 16;

function App() {
  const [activeSection, setActiveSection] = useState("home");
  const [operationsView, setOperationsView] = useState("guided");
  const [reservations, setReservations] = useState([]);
  const [datasetMeta, setDatasetMeta] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [apiReady, setApiReady] = useState(false);
  const [feedbackSummary, setFeedbackSummary] = useState(null);
  const [selectedReservation, setSelectedReservation] = useState(null);
  const [evaluationReservation, setEvaluationReservation] = useState(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isPageLoading, setIsPageLoading] = useState(false);
  const [bookingSearch, setBookingSearch] = useState("");
  const [bookingSearchError, setBookingSearchError] = useState("");
  const [isBookingSearchLoading, setIsBookingSearchLoading] = useState(false);
  const [workspaceError, setWorkspaceError] = useState("");

  const applyReservationPage = useCallback((data) => {
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
    setIsDetailOpen(false);
  }, []);

  const loadWorkspace = useCallback(async () => {
    setIsLoading(true);
    setApiReady(false);
    setWorkspaceError("");

    const [reservationsResult, modelResult, feedbackResult] = await Promise.allSettled([
      fetchPredictedReservations(RESERVATIONS_PAGE_SIZE, 0),
      fetchModelInfo(),
      fetchFeedbackSummary()
    ]);

    const errors = [];
    setApiReady([reservationsResult, modelResult, feedbackResult].some(
      (result) => result.status === "fulfilled"
    ));

    if (reservationsResult.status === "fulfilled") {
      applyReservationPage(reservationsResult.value);
    } else {
      errors.push("No se pudieron cargar y evaluar las reservas del backend.");
    }

    if (modelResult.status === "fulfilled") {
      setModelInfo(modelResult.value);
    } else {
      setModelInfo(null);
      errors.push("No se pudo consultar el estado del modelo.");
    }

    if (feedbackResult.status === "fulfilled") {
      setFeedbackSummary(feedbackResult.value);
    } else {
      errors.push("No se pudo consultar el resumen de feedback.");
    }

    setWorkspaceError(errors.join(" "));
    setIsLoading(false);
  }, [applyReservationPage]);

  const loadReservationPage = useCallback(async (offset) => {
    setIsPageLoading(true);
    setWorkspaceError("");

    try {
      const data = await fetchPredictedReservations(RESERVATIONS_PAGE_SIZE, offset);
      applyReservationPage(data);
      setApiReady(true);
    } catch {
      setApiReady(false);
      setWorkspaceError("No se pudo cargar y evaluar esta página de reservas.");
    } finally {
      setIsPageLoading(false);
    }
  }, [applyReservationPage]);

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

  async function searchReservation(event) {
    event.preventDefault();
    const bookingId = bookingSearch.trim().toUpperCase();
    setBookingSearch(bookingId);
    setBookingSearchError("");

    if (!/^INN\d{5}$/.test(bookingId)) {
      setBookingSearchError("Introduce un código con formato INN00000.");
      return;
    }

    setIsBookingSearchLoading(true);
    try {
      const reservation = await fetchPredictedReservationById(bookingId);
      setSelectedReservation(reservation);
      setEvaluationReservation(reservation);
      setIsDetailOpen(true);
      setApiReady(true);
    } catch (error) {
      setBookingSearchError(
        error.message === "Reservation not found."
          ? `No se encontró la reserva ${bookingId}.`
          : "No se pudo consultar la reserva en este momento."
      );
    } finally {
      setIsBookingSearchLoading(false);
    }
  }

  const modelReady = Boolean(modelInfo?.model_loaded);
  const systemReady = apiReady && modelReady;
  const systemStatusLabel = isLoading
    ? "Comprobando API y modelo"
    : !apiReady
      ? "API no disponible"
      : modelReady
        ? "API OK · Modelo cargado"
        : "API OK · Modelo no cargado";
  const reservationsLoading = isLoading || isPageLoading;
  const pageLimit = datasetMeta?.limit || RESERVATIONS_PAGE_SIZE;
  const pageOffset = datasetMeta?.offset || 0;
  const totalAvailable = datasetMeta?.totalAvailable || 0;
  const returnedOnPage = datasetMeta?.returned ?? reservations.length;
  const currentPage = Math.floor(pageOffset / pageLimit) + 1;
  const totalPages = Math.max(1, Math.ceil(totalAvailable / pageLimit));
  const visibleStart = returnedOnPage > 0 ? pageOffset + 1 : 0;
  const visibleEnd = pageOffset + returnedOnPage;

  function showPreviousPage() {
    loadReservationPage(Math.max(0, pageOffset - pageLimit));
  }

  function showNextPage() {
    loadReservationPage(pageOffset + pageLimit);
  }

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
            <button
              type="button"
              className={activeSection === "model" ? "active" : ""}
              onClick={() => showSection("model")}
            >
              <BrainCircuit size={18} />
              Modelo
            </button>
          </nav>

          <div className="system-status" aria-label="Estado del sistema">
            <button
              className={`status-badge system-health ${systemReady ? "ready" : "unavailable"}`}
              type="button"
              onClick={loadWorkspace}
              disabled={isLoading}
              title="Actualizar estado de la API y del modelo"
              aria-label={`${systemStatusLabel}. Actualizar estado`}
            >
              <RefreshCw size={16} className={isLoading ? "spin" : ""} />
              {systemStatusLabel}
            </button>
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
                  Muestra histórica priorizada con el modelo predictivo.
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
                    Muestra cargada
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
                  onClick={() => loadReservationPage(pageOffset)}
                  disabled={reservationsLoading}
                  aria-label="Actualizar página de reservas"
                  title="Actualizar página de reservas"
                >
                  <RefreshCw size={19} className={reservationsLoading ? "spin" : ""} />
                </button>
              </div>
            </div>

            <form className="booking-search" onSubmit={searchReservation}>
              <div>
                <Search size={18} />
                <label htmlFor="booking-search-input">Buscar por código de reserva</label>
              </div>
              <div className="booking-search-controls">
                <input
                  id="booking-search-input"
                  type="search"
                  value={bookingSearch}
                  onChange={(event) => setBookingSearch(event.target.value)}
                  placeholder="Ejemplo: INN02475"
                  autoComplete="off"
                  aria-describedby={bookingSearchError ? "booking-search-error" : undefined}
                />
                <button
                  className="primary-button"
                  type="submit"
                  disabled={isBookingSearchLoading}
                >
                  {isBookingSearchLoading ? "Buscando..." : "Buscar"}
                </button>
              </div>
              {bookingSearchError && (
                <p id="booking-search-error" role="alert">{bookingSearchError}</p>
              )}
            </form>

            <div className="metric-grid" aria-label="Resumen de reservas cargadas">
              <article>
                <Database size={20} />
                <span>Analizadas en esta página</span>
                <strong>{reservationsLoading ? "--" : reservations.length}</strong>
                <small>
                  {visibleStart.toLocaleString("es-ES")}–{visibleEnd.toLocaleString("es-ES")} de {totalAvailable.toLocaleString("es-ES")}
                </small>
              </article>
              <article className="metric-high">
                <AlertTriangle size={20} />
                <span>Riesgo alto</span>
                <strong>{reservationsLoading ? "--" : riskCounts.high}</strong>
                <small>revisión prioritaria</small>
              </article>
              <article className="metric-medium">
                <Activity size={20} />
                <span>Riesgo medio</span>
                <strong>{reservationsLoading ? "--" : riskCounts.medium}</strong>
                <small>seguimiento recomendado</small>
              </article>
              <article className="metric-low">
                <ShieldCheck size={20} />
                <span>Riesgo bajo</span>
                <strong>{reservationsLoading ? "--" : riskCounts.low}</strong>
                <small>observación normal</small>
              </article>
            </div>

            {operationsView === "guided" ? (
              <GuidedReservationFlow
                reservations={reservations}
                selectedReservation={selectedReservation}
                isLoading={reservationsLoading}
                onSelect={setSelectedReservation}
                onOpenDetail={openReservation}
                onEvaluate={evaluateReservation}
                pageOffset={pageOffset}
              />
            ) : operationsView === "all" ? (
              <ReservationsTable
                reservations={reservations}
                isLoading={reservationsLoading}
                onSelect={openReservation}
                onEvaluate={evaluateReservation}
              />
            ) : (
              <AlertsPanel
                reservations={reservations}
                isLoading={reservationsLoading}
                onSelect={openReservation}
                onEvaluate={evaluateReservation}
              />
            )}

            <nav className="pagination-bar" aria-label="Páginas de reservas">
              <div className="pagination-summary" aria-live="polite">
                <strong>Página {currentPage.toLocaleString("es-ES")} de {totalPages.toLocaleString("es-ES")}</strong>
                <span>
                  Reservas {visibleStart.toLocaleString("es-ES")}–{visibleEnd.toLocaleString("es-ES")} de {totalAvailable.toLocaleString("es-ES")}
                </span>
              </div>
              <div className="pagination-actions">
                <button
                  className="secondary-button"
                  type="button"
                  onClick={showPreviousPage}
                  disabled={reservationsLoading || pageOffset === 0}
                >
                  <ChevronLeft size={17} />
                  Anterior
                </button>
                <button
                  className="primary-button"
                  type="button"
                  onClick={showNextPage}
                  disabled={reservationsLoading || !datasetMeta?.hasMore}
                >
                  Siguiente
                  <ChevronRight size={17} />
                </button>
              </div>
            </nav>

            {datasetMeta?.source && (
              <p className="data-source">Fuente de datos: {datasetMeta.source}</p>
            )}
          </section>
        ) : activeSection === "model" ? (
          <ModelPage modelInfo={modelInfo} />
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

      <EducationalFooter />

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
