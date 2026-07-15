import React, { useCallback, useEffect, useState } from "react";
import {
  CalendarDays,
  Check,
  ClipboardCheck,
  Edit3,
  LoaderCircle,
  MessageSquareText,
  RefreshCw,
  Save,
  X
} from "lucide-react";
import { fetchFeedbackHistory, updateFeedbackRecord } from "../services/predictionService";
import "./FeedbackHistory.css";

const feedbackLabels = {
  correct: "Predicción correcta",
  incorrect: "Predicción incorrecta",
  unknown: "Sin confirmar"
};

const actualStatusLabels = {
  Canceled: "Cancelada",
  Not_Canceled: "No cancelada"
};

function formatDate(value) {
  if (!value) return "Fecha no disponible";
  return new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function stayDate(inputData) {
  if (!inputData) return "--";
  const month = String(inputData.arrival_month).padStart(2, "0");
  const day = String(inputData.arrival_date).padStart(2, "0");
  return `${day}/${month}/${inputData.arrival_year}`;
}

function editableValues(record) {
  return {
    user_feedback: record.user_feedback,
    actual_status: record.actual_status || "",
    comments: record.comments || ""
  };
}

function FeedbackHistory({ onFeedbackChanged }) {
  const [records, setRecords] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [draft, setDraft] = useState(null);
  const [savingId, setSavingId] = useState(null);
  const [saveError, setSaveError] = useState("");

  const loadHistory = useCallback(async () => {
    setIsLoading(true);
    setLoadError("");
    try {
      const response = await fetchFeedbackHistory();
      setRecords(response.records);
    } catch (error) {
      setLoadError(error.message || "No se pudo cargar el histórico de feedback.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  function startEditing(record) {
    setEditingId(record.record_id);
    setDraft(editableValues(record));
    setSaveError("");
  }

  function cancelEditing() {
    setEditingId(null);
    setDraft(null);
    setSaveError("");
  }

  async function saveChanges(recordId) {
    setSavingId(recordId);
    setSaveError("");
    try {
      const updated = await updateFeedbackRecord(recordId, {
        ...draft,
        actual_status: draft.actual_status || null,
        comments: draft.comments.trim() || null
      });
      setRecords((current) =>
        current.map((record) => (record.record_id === recordId ? updated : record))
      );
      cancelEditing();
      onFeedbackChanged?.();
    } catch (error) {
      setSaveError(error.message || "No se pudieron guardar los cambios.");
    } finally {
      setSavingId(null);
    }
  }

  return (
    <section className="feedback-history" aria-labelledby="feedback-history-title">
      <div className="feedback-history-header">
        <div>
          <h1 id="feedback-history-title">Histórico de feedback</h1>
        </div>
        <div className="feedback-history-actions">
          <span className="feedback-total">
            <ClipboardCheck size={18} />
            {records.length} {records.length === 1 ? "registro" : "registros"}
          </span>
          <button
            className="feedback-refresh"
            type="button"
            onClick={loadHistory}
            disabled={isLoading}
          >
            <RefreshCw size={17} className={isLoading ? "spin" : ""} />
            Actualizar
          </button>
        </div>
      </div>

      {loadError && <p className="feedback-history-error" role="alert">{loadError}</p>}

      {isLoading ? (
        <div className="feedback-history-state">
          <LoaderCircle className="spin" size={28} />
          <h2>Cargando feedbacks</h2>
          <p>Estamos recuperando el histórico guardado.</p>
        </div>
      ) : records.length === 0 ? (
        <div className="feedback-history-state empty">
          <MessageSquareText size={34} />
          <h2>Todavía no hay feedbacks</h2>
          <p>Los resultados confirmados desde “Evaluar reserva” aparecerán aquí.</p>
        </div>
      ) : (
        <div className="feedback-record-list">
          {records.map((record) => {
            const isEditing = editingId === record.record_id;
            const isSaving = savingId === record.record_id;

            return (
              <article className={`feedback-record ${record.user_feedback}`} key={record.record_id}>
                <div className="feedback-record-topline">
                  <div>
                    <span className={`feedback-result ${record.user_feedback}`}>
                      {record.user_feedback === "correct" ? <Check size={15} /> : <MessageSquareText size={15} />}
                      {feedbackLabels[record.user_feedback]}
                    </span>
                    <span className="feedback-created">
                      <CalendarDays size={14} />
                      {formatDate(record.created_at)}
                    </span>
                  </div>
                  {!isEditing && (
                    <button
                      className="feedback-edit"
                      type="button"
                      onClick={() => startEditing(record)}
                    >
                      <Edit3 size={16} />
                      Editar
                    </button>
                  )}
                </div>

                <div className="feedback-record-grid">
                  <div>
                    <span>Predicción original</span>
                    <strong>{actualStatusLabels[record.prediction]}</strong>
                    <small>{Math.round(record.probability * 100)} % de probabilidad</small>
                  </div>
                  <div>
                    <span>Resultado observado</span>
                    <strong>{record.actual_status ? actualStatusLabels[record.actual_status] : "Sin confirmar"}</strong>
                    <small>{record.risk_level === "high" ? "Riesgo alto" : record.risk_level === "medium" ? "Riesgo medio" : "Riesgo bajo"}</small>
                  </div>
                  <div>
                    <span>Contexto de la reserva</span>
                    <strong>{stayDate(record.input_data)}</strong>
                    <small>{record.input_data.market_segment_type} · {record.input_data.lead_time} días de antelación</small>
                  </div>
                  <div>
                    <span>Modelo</span>
                    <strong className="feedback-model-version">{record.model_version}</strong>
                    <small>Fuente: {record.source}</small>
                  </div>
                </div>

                {isEditing ? (
                  <div className="feedback-editor">
                    <label>
                      Valoración
                      <select
                        value={draft.user_feedback}
                        onChange={(event) => setDraft({ ...draft, user_feedback: event.target.value })}
                      >
                        <option value="correct">Predicción correcta</option>
                        <option value="incorrect">Predicción incorrecta</option>
                        <option value="unknown">Sin confirmar</option>
                      </select>
                    </label>
                    <label>
                      Resultado real
                      <select
                        value={draft.actual_status}
                        onChange={(event) => setDraft({ ...draft, actual_status: event.target.value })}
                      >
                        <option value="">Sin confirmar</option>
                        <option value="Canceled">Cancelada</option>
                        <option value="Not_Canceled">No cancelada</option>
                      </select>
                    </label>
                    <label className="feedback-editor-comments">
                      Comentarios
                      <textarea
                        maxLength={500}
                        value={draft.comments}
                        onChange={(event) => setDraft({ ...draft, comments: event.target.value })}
                        placeholder="Añade contexto sobre el resultado observado"
                      />
                    </label>
                    {saveError && <p className="feedback-save-error" role="alert">{saveError}</p>}
                    <div className="feedback-editor-actions">
                      <button type="button" className="feedback-cancel" onClick={cancelEditing} disabled={isSaving}>
                        <X size={16} />
                        Cancelar
                      </button>
                      <button type="button" className="feedback-save" onClick={() => saveChanges(record.record_id)} disabled={isSaving}>
                        {isSaving ? <LoaderCircle className="spin" size={16} /> : <Save size={16} />}
                        {isSaving ? "Guardando..." : "Guardar cambios"}
                      </button>
                    </div>
                  </div>
                ) : (
                  <p className="feedback-comments-display">
                    <strong>Comentarios:</strong> {record.comments || "Sin comentarios."}
                  </p>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

export default FeedbackHistory;
