# Hotel Insights

Sistema de clasificación para anticipar cancelaciones de reservas hoteleras.

Proyecto grupal del Bootcamp de Inteligencia Artificial de Factoría F5 Madrid.

---

## 1. Descripción

Hotel Insights es una solución de Machine Learning aplicada al sector hotelero.

El objetivo es predecir si una reserva será cancelada o no cancelada a partir de datos disponibles antes de la fecha de llegada. La predicción busca ayudar a equipos de reservas, revenue management y operaciones a tomar mejores decisiones sobre ocupación, ingresos y seguimiento comercial.

El proyecto combina:

- Machine Learning de clasificación.
- Análisis exploratorio de datos.
- Aplicación web.
- Documentación técnica.
- Presentación de negocio.
- Buenas prácticas de Git/GitHub.
- Metodología SDD / SPEC.
- Uso guiado de agentes de IA.

---

## 2. Problema de negocio

Las cancelaciones de reservas generan incertidumbre en la planificación hotelera.

Una plataforma de reservas u hotel puede usar un sistema predictivo para:

- Identificar reservas con alto riesgo de cancelación.
- Priorizar acciones de confirmación.
- Proteger ingresos.
- Optimizar ocupación.
- Mejorar la planificación operativa.

---

## 3. Dataset

Dataset seleccionado:

```text
Hotel Reservations Classification Dataset
```

Ruta local esperada:

```text
data/raw/hotel-reservations-classification-dataset/Hotel Reservations.csv
```

Target:

```text
booking_status
```

Clases esperadas:

```text
Canceled
Not_Canceled
```

El objetivo de clasificación es predecir si una reserva será cancelada.

---

## 4. Estado actual del proyecto

Estado actual:

- Dataset incorporado en `data/raw/`.
- Target definido como `booking_status`.
- Métrica principal definida: F1-score de la clase `Canceled`.
- Diccionario de datos inicial disponible en `reports/data_dictionary.md`.
- Notebooks iniciales de inspección y EDA disponibles en `notebooks/`.
- Frontend React + Vite integrado en `app/frontend`.
- Prototipo visual de producto disponible para validar la experiencia.
- Backend FastAPI inicial integrado en `app/backend`.
- Contrato API inicial documentado en `docs/api_contract.md`.
- Endpoint de salud disponible en `GET /health`.
- Endpoint de información de modelo disponible en `GET /model/info`.
- Endpoint de predicción real disponible en `POST /predict` usando el baseline Logistic Regression.
- Baseline reproducible entrenado y guardado en `models/baseline/logistic_regression_baseline.pkl`.
- Métricas y overfitting documentados en `reports/model_report.md`.
- Tests iniciales de API backend disponibles en `tests/test_backend_api.py`.
- Workflows de GitHub Actions creados para tests backend y build frontend.
- Configuración Docker inicial disponible para frontend y backend.
- Metodología SPEC creada en `.specify/`.
- Documentos de organización creados en `docs/project_management/`.
- Jira definido como herramienta oficial de gestión.
- Plantilla de Pull Request creada en `.github/pull_request_template.md`.
- Changelog creado en `CHANGELOG.md`.
- Tags iniciales creados y publicados.

Pendiente principal:

- Completar explicación de performance con feature importance y análisis de errores.
- Validar manualmente la app con entradas reales y capturas.
- Seleccionar Champion Model si se decide promocionar el challenger.
- Completar informe técnico.
- Validar Docker con el baseline real integrado.

---

## 5. Estructura del repositorio

```text
.
|-- .github/
|   |-- pull_request_template.md
|   `-- workflows/
|       |-- backend-tests.yml
|       `-- frontend-build.yml
|-- .specify/
|   |-- 1_intent.md
|   |-- 2_spec.md
|   |-- 3_plan.md
|   `-- 4_tasks.md
|-- app/
|   |-- backend/
|   |   |-- Dockerfile
|   |   |-- __init__.py
|   |   |-- main.py
|   |   `-- schemas.py
|   |-- components/
|   |-- frontend/
|   |   |-- Dockerfile
|   |   |-- nginx.conf
|   |   |-- src/
|   |   |-- package.json
|   |   |-- pnpm-lock.yaml
|   |   |-- pnpm-workspace.yaml
|   |   `-- vite.config.js
|   `-- pages/
|-- config/
|-- data/
|   `-- raw/
|-- docs/
|   |-- assets/
|   |-- business_presentation/
|   |-- project_management/
|   `-- technical_presentation/
|-- models/
|-- notebooks/
|-- reports/
|   `-- data_dictionary.md
|-- src/
|-- tests/
|-- CHANGELOG.md
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

El backend actual es una API FastAPI con endpoints:

```text
GET /health
GET /model/info
POST /predict
```

`GET /model/info` devuelve la versión y estado del modelo cargado. `POST /predict` usa el baseline Logistic Regression guardado en `models/baseline/logistic_regression_baseline.pkl`.

---

## 6. Frontend React

El frontend está en:

```text
app/frontend
```

Tecnologías:

- React.
- Vite.
- pnpm.
- CSS custom.
- Mock service de predicción.

Actualmente el frontend consulta el backend real por defecto. El mock editorial puede activarse solo para demos aisladas con `VITE_USE_MOCK_API=true`.

### Ejecutar frontend

Requisitos:

- Node.js LTS.
- pnpm.

Instalar pnpm si no está disponible:

```bash
npm install -g pnpm
```

Entrar al frontend:

```bash
cd app/frontend
```

Instalar dependencias:

```bash
pnpm install
```

Arrancar entorno local:

```bash
pnpm dev
```

Abrir en navegador:

```text
http://localhost:5173/
```

Crear build:

```bash
pnpm build
```

---

## 7. Entorno Python

Crear entorno virtual desde Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Comprobar Python activo:

```bash
which python
```

Desactivar entorno:

```bash
deactivate
```

---

## 8. Docker

El proyecto incluye una configuración Docker inicial para levantar frontend y backend en local.

Servicios:

- Backend FastAPI en `http://localhost:8000`.
- Frontend servido por nginx en `http://localhost:8080`.

Construir imágenes:

```bash
docker compose build
```

Levantar servicios:

```bash
docker compose up
```

Levantar servicios en segundo plano:

```bash
docker compose up -d
```

Parar servicios:

```bash
docker compose down
```

Comprobar backend:

```text
http://localhost:8000/health
```

Comprobar frontend:

```text
http://localhost:8080/
```

Nota: el backend actual carga el baseline Logistic Regression. Cuando se seleccione un Champion posterior, el servicio de inferencia deberá apuntar al nuevo artefacto versionado.

---

## 9. Metodología SPEC / SDD

El proyecto usa una metodología basada en SPEC / SDD.

Documentos principales:

```text
.specify/1_intent.md
.specify/2_spec.md
.specify/3_plan.md
.specify/4_tasks.md
```

La SPEC define:

- Intención del proyecto.
- Especificación técnica.
- Plan por fases.
- Backlog de tareas verificables.
- Criterios de cierre por nivel.

Antes de implementar cambios importantes, se debe revisar la SPEC.

El archivo `.specify/4_tasks.md` funciona como checklist vivo del proyecto.

Estados utilizados:

```text
[ ] pendiente
[~] en progreso
[x] completada y verificada
[!] bloqueada
[-] cancelada/no aplica
```

Estado actual destacado:

```text
[x] T-0.1 Crear tablero de gestion
[x] T-0.2 Revisar y aceptar SPEC inicial
[-] T-0.3 Definir candidatos de dataset
[x] T-0.4 Disenar mock funcional de app
[x] T-1.1 Elegir dataset definitivo
[~] T-1.2 Definir target y clases
[x] T-1.3 Crear diccionario de datos
[~] T-1.4 Realizar EDA inicial
[~] T-2.5 Crear app minima de prediccion
[~] T-4.3 Dockerizar app
[~] T-4.5 Documentar instalacion y ejecucion
```

---

## 10. Documentación de organización

Documentos de organización del proyecto:

```text
docs/project_management/00_project_vision.md
docs/project_management/01_git_workflow.md
docs/project_management/02_sdd_ai_agents.md
docs/project_management/03_delivery_roadmap.md
```

Estos documentos explican:

- Visión del producto.
- Flujo Git.
- Uso de agentes de IA.
- Roadmap de entrega.
- Organización profesional del proyecto.

---

## 11. Flujo Git

Ramas principales:

```text
main
develop
```

Reglas:

- No trabajar directamente en `main`.
- `main` queda reservada para la entrega final estable.
- `develop` es la rama principal de integración durante el desarrollo.
- Crear ramas desde `develop`.
- Abrir Pull Request hacia `develop`.
- Usar commits descriptivos.
- No subir carpetas generadas como `node_modules/`, `dist/`, `.venv/` o archivos `.env`.

Ejemplo:

```bash
git switch develop
git pull origin develop
git switch -c feature/nombre-tarea
```

Subir rama:

```bash
git push -u origin feature/nombre-tarea
```

Crear PR:

```text
base: develop
compare: feature/nombre-tarea
```

---

## 12. Pull Requests

El repositorio incluye una plantilla de Pull Request en:

```text
.github/pull_request_template.md
```

Cada PR debe indicar:

- Resumen del cambio.
- Tarea SPEC relacionada.
- Tipo de cambio.
- Verificación realizada.
- Evidencias o capturas si aplica.
- Pendientes.
- Checklist de buenas prácticas.

Tipos de cambio contemplados:

- Documentation.
- Frontend.
- Backend.
- ML / Data.
- Tests.
- CI / DevOps.
- Refactor.
- Other.

---

## 13. Changelog y tags

El repositorio incluye:

```text
CHANGELOG.md
```

El changelog resume hitos relevantes del proyecto. No sustituye al historial de commits ni a `.specify/4_tasks.md`.

Tags creados:

```text
v0.1.0-docs-foundation
v0.2.0-frontend-mock
```

Significado:

- `v0.1.0-docs-foundation`: base documental, SPEC, roadmap, flujo Git, README inicial, PR template y changelog.
- `v0.2.0-frontend-mock`: frontend React + Vite con mock funcional de predicción.

Hitos previstos:

```text
v0.3.0-data-eda
v0.4.0-baseline
v0.5.0-api
v0.6.0-champion
v0.7.0-operational
v1.0.0-final
```

---

## 14. Jira

La herramienta oficial de gestión es Jira.

Tablero del proyecto:

```text
https://miguel-redondo.atlassian.net/jira/software/projects/G2PC/boards/100/backlog
```

Los tickets deben mantenerse alineados con:

```text
.specify/4_tasks.md
```

---

## 15. Roles del equipo

Roles sugeridos por la SPEC:

| Rol | Responsabilidad principal |
| --- | --- |
| ML Core | Dataset, EDA, preprocessing, modelos, métricas |
| App / Producto | Frontend, app, integración, feedback, demo |
| MLOps / Experto | Tests, Docker, CI/CD, drift, Champion/Challenger |
| QA / Docs / Presentación | README, informe, checklist, capturas, presentaciones |

Los roles son colaborativos. Cada integrante puede apoyar tareas de otros bloques, pero evitando mezclar cambios no relacionados en el mismo PR.

---

## 16. Niveles de entrega y progreso

Leyenda:

```text
[x] completado o base funcional verificada
[~] en progreso
[ ] pendiente
```

### Nivel Esencial

| Estado | Requisito | Evidencia actual | Pendiente |
| --- | --- | --- | --- |
| [x] | Modelo funcional de clasificación | Baseline Logistic Regression entrenado con Pipeline de Scikit-learn y guardado en `models/baseline/logistic_regression_baseline.pkl`. | Seleccionar Champion posterior si se decide avanzar a Nivel Medio. |
| [~] | EDA con visualizaciones relevantes para clasificación | Notebooks iniciales de inspección y EDA en `notebooks/`; diccionario en `reports/data_dictionary.md`. | Cerrar conclusiones de negocio, visualizaciones finales y análisis de desbalance. |
| [x] | Overfitting inferior al 5% | Baseline gap F1 `0.0079`; Random Forest gap F1 `0.0186`, ambos bajo el límite `0.05`. | Mantener control al elegir Champion final. |
| [x] | Solución productivizada | Frontend React + Vite, backend FastAPI, contrato `POST /predict`, endpoint `GET /model/info`, Docker local y baseline real integrado. | Validación manual y despliegue posterior. |
| [~] | Informe técnico de rendimiento | Métricas, matriz de confusión, curva ROC y overfitting documentados en `reports/model_report.md`. | Añadir feature importance y análisis de errores. |

### Nivel Medio

| Estado | Requisito | Evidencia actual | Pendiente |
| --- | --- | --- | --- |
| [ ] | Modelo con técnicas de ensemble | En roadmap ML. | Entrenar y comparar Random Forest, Gradient Boosting u otras alternativas. |
| [ ] | Validación cruzada | En roadmap ML. | Definir estrategia de validación y registrar resultados. |
| [ ] | Optimización de hiperparámetros | En roadmap ML. | Aplicar GridSearch, RandomSearch, Optuna u otra técnica acordada. |
| [ ] | Recogida de feedback para monitorizar performance | Previsto en contrato producto/MLOps. | Diseñar almacenamiento y métrica de feedback en la app. |
| [ ] | Recogida de datos nuevos para futuros reentrenamientos | Previsto como mejora de producto. | Definir pipeline de ingestión y persistencia. |

### Nivel Avanzado

| Estado | Requisito | Evidencia actual | Pendiente |
| --- | --- | --- | --- |
| [~] | Versión dockerizada del programa | `docker-compose.yml`, Dockerfile backend, Dockerfile frontend y nginx configurados. | Integrar modelo real dentro del flujo Docker. |
| [ ] | Guardado en base de datos de datos recogidos | No implementado todavía. | Elegir base de datos y definir esquema mínimo. |
| [ ] | Despliegue web | Preparación local con Docker. | Definir plataforma y variables de entorno de despliegue. |
| [~] | Tests unitarios | Tests smoke de API backend y workflows CI activos. | Añadir tests de preprocessing, métricas mínimas y modelo. |

### Nivel Experto

| Estado | Requisito | Evidencia actual | Pendiente |
| --- | --- | --- | --- |
| [ ] | Experimentos con redes neuronales | No iniciado. | Valorar si aporta frente a modelos clásicos. |
| [ ] | A/B Testing para comparar modelos | Documentado como posibilidad MLOps. | Definir Champion/Challenger y reparto de tráfico o evaluación offline. |
| [ ] | Monitorización de Data Drift | Documentado como objetivo experto. | Definir variables a monitorizar y umbrales de alerta. |
| [ ] | Auto-reemplazo condicionado de modelos | Documentado como objetivo experto. | Diseñar política de promoción solo si el nuevo modelo supera métricas mínimas. |

---

## 17. Roadmap resumido

1. Organización y acuerdos.
2. Dataset, EDA y contrato de datos.
3. MVP esencial.
4. Modelo robusto y feedback.
5. Tests, CI y Docker.
6. Capa MLOps experta.
7. Cierre, informe y presentaciones.

Detalle completo:

```text
docs/project_management/03_delivery_roadmap.md
```

---

## 18. Próximos pasos técnicos

Prioridades inmediatas:

1. Cerrar distribución del target y desbalance.
2. Consolidar EDA y visualizaciones finales.
3. Aplicar F1-score de la clase `Canceled` como métrica principal.
4. Consolidar pipeline de preprocesamiento.
5. Completar feature importance y análisis de errores.
6. Validar manualmente frontend + backend + modelo real.
7. Ampliar tests de preprocessing, modelo y métricas.
10. Preparar informe técnico.
11. Preparar presentación de negocio y presentación técnica.
12. Decidir siguiente capa avanzada: persistencia, despliegue o monitorización.

---

## 19. Sprint 1

Sprint 1 se considera orientado a dejar preparada la base del proyecto:

- Repositorio ordenado.
- Dataset incorporado.
- SPEC inicial creada.
- Documentación de organización creada.
- Jira definido como herramienta de gestión.
- Frontend mock integrado.
- Contrato API inicial creado.
- Backend FastAPI base creado.
- Endpoints `GET /health`, `GET /model/info` y `POST /predict` creados.
- Tests iniciales de API backend creados.
- CI inicial para backend y frontend creado.
- Docker local inicial para frontend y backend creado.
- Flujo Git definido.
- Plantilla de PR creada.
- Changelog y tags iniciales creados.

Queda para Sprint 2:

- Pipeline de preprocesamiento.
- Baseline ML.
- Métricas y overfitting.
- Integración real del modelo en backend.
- Conexión frontend-backend contra inferencia real.
- Tests de preprocessing, modelo y métricas.
- Persistencia o feedback de predicciones si el alcance lo permite.
- Preparación de despliegue.

---

## 20. Verificaciones útiles

Estado de Git:

```bash
git status
```

Actualizar `develop`:

```bash
git switch develop
git pull origin develop
```

Ver ramas:

```bash
git branch -a
```

Ver tags:

```bash
git tag --list
```

Ver archivos modificados:

```bash
git diff --name-only
```

Comprobar problemas básicos de diff:

```bash
git diff --check
```

---

## 21. Equipo

Proyecto desarrollado por el Grupo 2 del Bootcamp de Inteligencia Artificial de Factoría F5 Madrid.

---

## 22. Nota

Este README describe el estado y la dirección del proyecto. Debe actualizarse cada vez que cambien la forma de ejecutar la app, el modelo Champion, la arquitectura, los entregables principales, los hitos versionados o el flujo de trabajo del equipo.
