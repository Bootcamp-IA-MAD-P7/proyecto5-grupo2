# Delivery Roadmap - Hotel Insights

## 1. Objetivo

Este roadmap organiza el desarrollo del proyecto por fases, evitando mezclar tareas esenciales con mejoras avanzadas.

La prioridad es construir primero una entrega mínima sólida y demostrable. Después se añaden mejoras de producto, MLOps, Docker, tests y presentación.

## 2. Principio de planificación

El proyecto se desarrollará con esta regla:

```text
Primero estable, después sofisticado.
```

No se debe bloquear el Nivel Esencial por intentar implementar Nivel Experto demasiado pronto.

## 3. Fase 0 - Organización y acuerdos

Objetivo:

- Alinear visión del producto.
- Definir flujo Git.
- Definir uso de metodología SDD / SPEC.
- Definir uso de agentes IA.
- Preparar una propuesta de arquitectura profesional.

Entregables:

- `docs/project_management/00_project_vision.md`
- `docs/project_management/01_git_workflow.md`
- `docs/project_management/02_sdd_ai_agents.md`
- `docs/project_management/03_delivery_roadmap.md`
- `.github/pull_request_template.md`
- `CHANGELOG.md`
- Tags `v0.1.0-docs-foundation` y `v0.2.0-frontend-mock`

Criterio de cierre:

- El equipo entiende cómo se trabajará.
- No se toca código funcional.
- Todo entra por Pull Request a `develop`.

Estado actual:

- Fase de organizacion cerrada en `develop`.
- Flujo de Pull Requests documentado.
- Changelog y tags iniciales creados.
- Jira definido como herramienta oficial de gestion.

## 4. Fase 1 - Dataset, EDA y contrato de datos

Objetivo:

- Confirmar dataset definitivo.
- Confirmar target.
- Documentar features.
- Hacer EDA inicial.
- Crear contrato de datos para modelo y app.

Entregables:

- Dataset en `data/raw/`.
- Diccionario de datos.
- Notebook de inspección.
- Notebook de EDA.
- Visualizaciones relevantes.
- Primera lista de features.
- Actualización de `.specify/2_spec.md`.

Criterio de cierre:

- El equipo puede explicar qué se predice, con qué columnas y por qué.
- No hay leakage evidente sin documentar.
- El contrato de inputs está claro para App / Producto.

Estado actual:

- Dataset definitivo disponible en `data/raw/`.
- Diccionario de datos inicial disponible en `reports/data_dictionary.md`.
- Notebooks iniciales disponibles en `notebooks/`.
- EDA exploratorio disponible en `notebooks/02_eda_exploratory.ipynb` con distribucion del target, desbalance, histogramas, relaciones con target, matriz de correlacion y conclusiones.
- Contrato de inputs alineado con el modelo productivizado.
- Pendiente: reutilizar las visualizaciones clave en presentacion de negocio si el equipo lo necesita.

## 5. Fase 2 - MVP esencial

Objetivo:

Construir una primera solución completa de extremo a extremo.

Incluye:

- Pipeline de preprocesamiento.
- Baseline ML.
- Métrica principal: F1-score de la clase `Canceled`.
- Métricas obligatorias.
- Control de overfitting.
- App funcional.
- Informe técnico inicial.

Entregables:

- Script o notebook reproducible de baseline.
- Métricas train/validación.
- Matriz de confusión.
- Curva ROC si aplica.
- App que reciba inputs y devuelva predicción.
- Informe técnico inicial.
- README con instalación y ejecución.

Criterio de cierre:

- La app funciona.
- El modelo predice.
- El overfitting medido con F1-score de la clase `Canceled` está por debajo del 5% o queda documentado como bloqueo.
- Otra persona puede ejecutar el proyecto siguiendo el README.

Estado actual:

- Frontend React + Vite integrado en `app/frontend`.
- Backend FastAPI inicial integrado en `app/backend`.
- Contrato API inicial documentado en `docs/api_contract.md`.
- Endpoint `GET /health`, `GET /model/info`, `GET /reservations/demo`, `POST /predict`, `POST /feedback` y `GET /feedback/summary` disponibles.
- `POST /predict` usa el Champion Random Forest guardado en `models/champion/random_forest_champion.pkl`.
- `GET /reservations/demo` sirve reservas candidatas desde el CSV real para alimentar el frontend principal.
- El frontend principal consume reservas reales, predicciones reales y feedback real.
- Informe tecnico disponible en `reports/model_report.md` con metricas, overfitting, curva ROC, matriz de confusion, feature importance y analisis de errores del Champion.
- Docker validado en local y desplegado en Amazon EC2 para frontend y backend.
- Nivel Esencial cubierto; validacion manual funcional documentada en `reports/manual_app_validation.md`.

## 6. Fase 3 - Nivel medio

Objetivo:

Mejorar el modelo y el producto.

Incluye:

- Modelo ensemble.
- Validación cruzada.
- Tuning de hiperparámetros.
- Selección de Champion Model.
- Feedback de usuario.
- Registro de predicciones.

Entregables:

- Modelo ensemble comparado con baseline.
- Tabla de experimentos.
- Champion Model versionado.
- Feature importance o explicación equivalente.
- Feedback guardado en CSV, SQLite o base equivalente.
- Informe técnico actualizado.

Criterio de cierre:

- Champion supera o justifica su elección frente al baseline usando F1-score de la clase `Canceled` como métrica principal.
- Champion cumple overfitting inferior al 5%.
- La app muestra versión del modelo y permite registrar feedback.

Estado actual:

- Random Forest optimizado, comparado contra baseline y seleccionado como Champion.
- Validacion cruzada estratificada de 3 folds documentada con F1 medio `0.8160`.
- Tuning de hiperparametros consolidado en script reproducible.
- Feedback implementado con `POST /feedback` y `GET /feedback/summary`.
- Recogida de datos nuevos para futuros reentrenamientos cubierta con SQLAlchemy, SQLite local, PostgreSQL RDS e ingesta en `src/data/feedback_ingestion.py`.
- Estado: Nivel Medio cubierto.

## 7. Fase 4 - Nivel avanzado operativo

Objetivo:

Preparar el proyecto para ejecución más profesional.

Incluye:

- Tests mínimos.
- Docker.
- GitHub Actions.
- Persistencia más robusta.
- Smoke test documentado.
- Despliegue web reproducible.

Entregables:

- Tests de preprocessing.
- Tests de métricas.
- Test de inferencia.
- Dockerfile.
- `docker-compose.yml` si aplica.
- Workflow de CI para Python.
- Workflow de CI para frontend.
- Checklist de validación manual.
- PostgreSQL administrado.
- Despliegue HTTPS y entrega automática desde `develop`.

Criterio de cierre:

- Los tests pasan.
- La app puede arrancar con comandos documentados.
- GitHub Actions verifica cambios básicos.
- Docker queda funcional o documentado como limitación.

Estado actual:

- Tests backend y build frontend verificados por GitHub Actions.
- Docker Compose validado en local y en EC2.
- PostgreSQL desplegado en Amazon RDS privado.
- CloudFront publica la app mediante HTTPS.
- GitHub Actions despliega automáticamente en EC2 mediante OIDC y SSM.
- Guía operativa disponible en `docs/aws_deployment.md`.
- Estado: Nivel Avanzado cubierto.

## 8. Fase 5 - Nivel experto / MLOps

Objetivo:

Añadir componentes expertos sin romper el sistema esencial.

Incluye:

- Red neuronal experimental.
- Champion/Challenger.
- A/B Testing real o simulado.
- Data Drift mediante perfil de entrenamiento versionado, PSI y endpoint de monitorizacion. Completado.
- Auto-reemplazo condicionado.

Entregables:

- Modelo Challenger.
- Comparación Champion vs Challenger.
- Script y endpoint de reporte de drift.
- Reglas de promoción de modelos.
- Diagrama de ciclo MLOps.
- Documentación de limitaciones.

Criterio de cierre:

- Ningún modelo reemplaza al Champion sin cumplir reglas.
- La red neuronal se compara con las mismas métricas.
- El drift genera alerta, no reemplazo automático.
- La capa experta queda explicada para defensa técnica.

## 9. Fase 6 - Cierre y defensa

Objetivo:

Congelar una versión final demostrable.

Incluye:

- Validación final.
- Informe técnico.
- Presentación de negocio.
- Presentación técnica.
- Capturas.
- Checklist de entrega.
- Tag final.

Entregables:

- README final.
- Informe técnico final.
- Presentación cliente/negocio.
- Presentación técnica.
- Capturas de app.
- Checklist de consigna.
- Tag `v1.0.0-final`.

Criterio de cierre:

- La demo funciona.
- Las métricas coinciden entre código, informe y presentación.
- El repositorio está ordenado.
- No se prometen funcionalidades que no existan.
- El equipo sabe defender cada parte.

## 10. Orden recomendado de próximos PRs

Con los niveles Esencial, Medio y Avanzado cubiertos, se recomienda cerrar el proyecto con PRs pequeños:

```text
docs/ux-ui-visual-identity
docs/business-presentation
docs/technical-presentation
docs/final-delivery-checklist
```

Las tareas de Nivel Experto deben ir en ramas separadas y solo se incorporarán si no comprometen la demo estable ni el cierre documental.

Cada PR debe tener una verificación clara y no mezclar responsabilidades.
