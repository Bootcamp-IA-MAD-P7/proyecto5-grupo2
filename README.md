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
- Notebooks iniciales de inspección y EDA.
- Diccionario de datos inicial.
- Frontend React integrado en `app/frontend`.
- Metodología SPEC creada en `.specify/`.
- Documentos de organización del proyecto creados en `docs/project_management/`.

Pendiente principal:

- Definir métrica principal.
- Consolidar pipeline de preprocesamiento.
- Entrenar baseline reproducible.
- Seleccionar Champion Model.
- Crear backend de inferencia.
- Conectar frontend con predicción real.
- Completar informe técnico.
- Añadir tests, CI y Docker si el avance lo permite.

---

## 5. Estructura del repositorio

```text
.
├── .specify/                  # Metodología SPEC / SDD
├── app/
│   ├── components/            # Componentes base existentes
│   ├── frontend/              # Frontend React + Vite
│   └── pages/                 # Páginas base existentes
├── config/                    # Configuración del proyecto
├── data/
│   └── raw/                   # Dataset original
├── docs/
│   ├── assets/                # Recursos visuales y capturas
│   ├── business_presentation/ # Material para presentación de negocio
│   ├── project_management/    # Organización, Git, SDD y roadmap
│   └── technical_presentation/# Material para presentación técnica
├── models/                    # Modelos entrenados y artefactos
├── notebooks/                 # EDA e inspección de datos
├── reports/                   # Informes, diccionario de datos y figuras
├── src/                       # Código ML reutilizable
├── tests/                     # Tests
├── requirements.txt           # Dependencias Python
└── README.md
```

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

## 8. Metodología SPEC / SDD

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

---

## 9. Documentación de organización

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

---

## 10. Flujo Git

Ramas principales:

```text
main
develop
```

Reglas:

- No trabajar directamente en `main`.
- No trabajar directamente en `develop` salvo acuerdo puntual.
- Crear ramas desde `develop`.
- Abrir Pull Request hacia `develop`.
- Usar commits descriptivos.

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

## 11. Roles del equipo

Roles sugeridos por la SPEC:

| Rol | Responsabilidad principal |
| --- | --- |
| ML Core | Dataset, EDA, preprocessing, modelos, métricas |
| App / Producto | Frontend, app, integración, feedback, demo |
| MLOps / Experto | Tests, Docker, CI/CD, drift, Champion/Challenger |
| QA / Docs / Presentación | README, informe, checklist, capturas, presentaciones |

---

## 12. Niveles de entrega

### Nivel Esencial

- Modelo funcional de clasificación.
- EDA con visualizaciones.
- Overfitting inferior al 5%.
- App productivizada.
- Informe técnico con métricas de clasificación.

### Nivel Medio

- Ensemble.
- Validación cruzada.
- Tuning de hiperparámetros.
- Feedback o registro de predicciones.

### Nivel Avanzado

- Docker.
- Persistencia.
- Tests unitarios.
- Despliegue o preparación para despliegue.

### Nivel Experto

- Red neuronal experimental.
- A/B Testing.
- Data Drift.
- Auto-reemplazo condicionado de modelos.

---

## 13. Roadmap resumido

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

## 14. Próximos pasos técnicos

Prioridades inmediatas:

1. Definir métrica principal.
2. Consolidar pipeline de preprocesamiento.
3. Entrenar baseline reproducible.
4. Registrar métricas y overfitting.
5. Crear backend de inferencia.
6. Conectar frontend con modelo real.
7. Documentar ejecución completa.
8. Añadir tests mínimos.
9. Preparar informe técnico.

---

## 15. Equipo

Proyecto desarrollado por el Grupo 2 del Bootcamp de Inteligencia Artificial de Factoría F5 Madrid.

---

## 16. Nota

Este README describe el estado y la dirección del proyecto. Debe actualizarse cada vez que cambien la forma de ejecutar la app, el modelo Champion, la arquitectura o los entregables principales.