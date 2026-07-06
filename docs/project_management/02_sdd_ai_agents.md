# SDD And AI Agents Workflow - Hotel Insights

## 1. Objetivo

Este documento define cómo usaremos metodología SDD / SPEC y agentes de IA para trabajar de forma ordenada, trazable y segura.

El objetivo no es sustituir el criterio del equipo, sino usar la IA como apoyo técnico, documental y de revisión.

## 2. Fuente de verdad del proyecto

Antes de iniciar cualquier tarea relevante, se deben revisar estos archivos:

```text
.specify/1_intent.md
.specify/2_spec.md
.specify/3_plan.md
.specify/4_tasks.md
README.md
```

La carpeta `.specify/` define:

- Qué se quiere construir.
- Qué está dentro y fuera de alcance.
- Qué fases existen.
- Qué criterios de verificación aplican.
- Qué tareas corresponden a cada rol.

Si una propuesta contradice la SPEC, primero debe discutirse y actualizarse la SPEC.

## 3. Principio principal

Primero se protege el Nivel Esencial:

- Dataset documentado.
- Target definido.
- EDA.
- Modelo funcional.
- Métricas obligatorias.
- Overfitting inferior al 5%.
- App funcional.
- Informe técnico.
- README ejecutable.

Después se añaden mejoras de Nivel Medio, Avanzado y Experto.

Ninguna tarea avanzada debe romper o bloquear el MVP esencial.

## 4. Agentes propuestos

Se proponen cuatro tipos de agentes, alineados con los roles del equipo.

### Agente ML Core

Responsable de apoyar en:

- Dataset.
- EDA.
- Preprocessing.
- Baseline.
- Ensemble.
- Validación cruzada.
- Tuning.
- Champion Model.
- Métricas.
- Análisis de errores.

No debe modificar frontend, Docker o presentación salvo coordinación explícita.

### Agente App / Producto

Responsable de apoyar en:

- Frontend.
- Formulario de inputs.
- Integración con backend/modelo.
- Pantalla de resultado.
- Feedback.
- Experiencia de usuario.
- Demo funcional.

No debe inventar features ni cambiar el contrato del modelo sin validarlo con ML Core.

### Agente MLOps / Experto

Responsable de apoyar en:

- Tests.
- Docker.
- GitHub Actions.
- Versionado de modelos.
- Champion/Challenger.
- A/B Testing.
- Data Drift.
- Auto-reemplazo condicionado.

No debe bloquear la entrega esencial por implementar componentes expertos.

### Agente QA / Docs / Presentación

Responsable de apoyar en:

- README.
- Checklist.
- Documentación.
- Tabla de experimentos.
- Capturas.
- Validación manual.
- Presentación de negocio.
- Presentación técnica.

No debe ser responsable único de decisiones críticas de modelo, app productiva o MLOps.

## 5. Reglas para trabajar con IA

Antes de pedir cambios a un agente, indicar:

- Rama actual.
- Rol del agente.
- Tarea SPEC relacionada.
- Archivos que puede tocar.
- Qué no debe tocar.
- Criterio de verificación.

Ejemplo:

```text
Actúa como Agente App / Producto.
Rama: feature/app-feedback.
Tarea SPEC: T-3.6 Implementar feedback.
Puedes tocar app/frontend y app/backend.
No modifiques src/models ni notebooks.
Debes dejar comando de verificación.
```

## 6. Formato mínimo de respuesta esperado

Después de cada avance, el agente debe indicar:

```text
Archivos modificados:
-

Tarea SPEC relacionada:
-

Cómo verificar:
-

Pendiente:
-
```

## 7. Trabajo por ramas

Cada agente o integrante debe trabajar en una rama específica:

```text
feature/ml-baseline
feature/backend-predict-api
feature/app-feedback
docs/readme-installation
test/preprocessing-pipeline
ci/frontend-build
```

Todo cambio debe entrar por Pull Request hacia `develop`.

## 8. Qué puede hacer la IA

La IA puede ayudar a:

- Proponer estructura.
- Escribir documentación.
- Crear boilerplate.
- Revisar código.
- Detectar inconsistencias.
- Crear tests.
- Mejorar UX/UI.
- Preparar presentaciones.
- Redactar informes.

## 9. Qué no debe hacer la IA sin revisión

La IA no debe decidir sola:

- Dataset definitivo.
- Target final.
- Métrica principal.
- Champion Model.
- Eliminación de features.
- Merge a `develop`.
- Merge a `main`.
- Tags finales.
- Promoción automática de modelos.
- Cambios que afecten al trabajo de otro rol.

## 10. Evidencia de verificación

Cada tarea debe dejar alguna evidencia:

- Comando ejecutado.
- Test pasado.
- Captura.
- Métrica.
- Notebook reproducible.
- Documento actualizado.
- Registro en tabla de experimentos.
- Validación manual.

## 11. Relación con la presentación final

La documentación generada por los agentes debe alimentar:

- README.
- Informe técnico.
- Presentación de negocio.
- Presentación técnica.
- Checklist final.

La presentación no debe prometer funcionalidades que no existan en código o documentación.

## 12. Regla de seguridad del proyecto

Si una mejora no ayuda a cerrar la entrega esencial o no puede verificarse, se deja como propuesta futura.

El proyecto debe priorizar una demo estable antes que una arquitectura ambiciosa incompleta.