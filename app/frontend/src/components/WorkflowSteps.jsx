import React from "react";
import { Check, ClipboardCheck, ListChecks, Sparkles } from "lucide-react";
import "./WorkflowSteps.css";

const steps = [
  { number: 1, label: "Priorizar", icon: ListChecks },
  { number: 2, label: "Evaluar", icon: Sparkles },
  { number: 3, label: "Registrar resultado", icon: ClipboardCheck }
];

function WorkflowSteps({ activeStep, completedThrough = activeStep - 1, onReturnToQueue }) {
  return (
    <nav className="workflow-steps" aria-label="Flujo de revisión">
      <ol>
        {steps.map((step) => {
          const Icon = step.icon;
          const isComplete = step.number <= completedThrough;
          const isActive = step.number === activeStep;
          const content = (
            <>
              <span className="workflow-step-icon">
                {isComplete ? <Check size={17} /> : <Icon size={17} />}
              </span>
              <span>
                <small>Paso {step.number}</small>
                <strong>{step.label}</strong>
              </span>
            </>
          );

          return (
            <li
              className={`${isActive ? "active" : ""} ${isComplete ? "complete" : ""}`}
              key={step.number}
              aria-current={isActive ? "step" : undefined}
            >
              {step.number === 1 && onReturnToQueue ? (
                <button type="button" onClick={onReturnToQueue}>
                  {content}
                </button>
              ) : (
                <div>{content}</div>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

export default WorkflowSteps;
