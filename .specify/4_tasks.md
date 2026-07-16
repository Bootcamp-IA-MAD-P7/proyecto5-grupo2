# SPEC 4 - Tasks

Este backlog debe mantenerse alineado con Jira. Cada ticket debe moverse de estado solo cuando su criterio de verificacion este cumplido.

## Protocolo de ejecucion

1. Antes de empezar un ticket, revisar dependencias.
2. Crear o usar una rama con nombre descriptivo.
3. Tocar solo los archivos indicados o actualizar el ticket si cambia el alcance.
4. Registrar evidencia de verificacion.
5. Actualizar README, informe o tabla de experimentos si el cambio afecta al uso del proyecto.
6. Pedir revision tecnica en tickets criticos.

## Leyenda de estados

- `[ ]` pendiente.
- `[~]` en progreso.
- `[x]` completada y verificada.
- `[!]` bloqueada.
- `[-]` cancelada/no aplica.

## Roles sugeridos

- I1 - ML Core.
- I2 - App / Producto.
- I3 - MLOps / Experto.
- I4 - QA / Docs / Presentacion, integrante junior con tareas guiadas.

## Fase 0 - Preparacion

### [x] T-0.1 Crear tablero de gestion

- Archivos afectados: `.specify/2_spec.md`.
- Accion: crear Jira o herramienta equivalente con columnas Backlog, In Progress, Review, Done y Blocked.
- Responsable sugerido: I4.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: ninguna.
- Criterio de verificacion: tablero creado con tickets iniciales y enlace documentado.
- Comando de verificacion: no aplica.
- Evidencia: Jira oficial documentado en `.specify/2_spec.md`.

### [x] T-0.2 Revisar y aceptar SPEC inicial

- Archivos afectados: `.specify/`.
- Accion: leer los cuatro documentos SPEC y anotar dudas o cambios.
- Responsable sugerido: todo el equipo, coordinado por I4.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: `.specify/` creado.
- Criterio de verificacion: acuerdos registrados y TODO principales identificados.
- Comando de verificacion: no aplica.
- Evidencia: SPEC actualizada con stack React + Vite, FastAPI previsto y Jira oficial.

### [-] T-0.3 Definir candidatos de dataset

- Archivos afectados: `.specify/2_spec.md`, `README.md`.
- Accion: listar 2 o 3 datasets candidatos con target posible, fuente, ventajas y riesgos.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: con apoyo.
- Dependencias: T-0.2.
- Criterio de verificacion: el equipo puede elegir dataset con criterios claros.
- Comando de verificacion: no aplica.
- Nota de estado: no aplica ya como tarea activa; el dataset definitivo de reservas hoteleras ya fue seleccionado.

### [x] T-0.4 Disenar mock funcional de app

- Archivos afectados: `app/frontend/`, `.specify/2_spec.md`.
- Accion: definir pantallas minimas de app: formulario, resultado, feedback y version de modelo.
- Responsable sugerido: I2.
- Dificultad: baja.
- Apto junior: con apoyo visual.
- Dependencias: dataset definitivo seleccionado.
- Criterio de verificacion: flujo de app entendido por todo el equipo.
- Comando de verificacion: `cd app/frontend && pnpm install && pnpm dev`.
- Evidencia: frontend React + Vite integrado en `app/frontend` y mergeado en `develop`.

## Fase 1 - Dataset y EDA

### [x] T-1.1 Elegir dataset definitivo

- Archivos afectados: `.specify/2_spec.md`, `README.md`, `data/raw/` si aplica.
- Accion: seleccionar dataset, documentar fuente y forma de descarga.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-0.3.
- Criterio de verificacion: dataset accesible y target posible.
- Evidencia: dataset incorporado en `data/raw/hotel-reservations-classification-dataset/Hotel Reservations.csv` con 36.275 filas y 19 columnas.
- Comando de verificacion: `Test-Path "data/raw/hotel-reservations-classification-dataset/Hotel Reservations.csv"`.

### [x] T-1.2 Definir target y clases

- Archivos afectados: `.specify/2_spec.md`, `reports/model_report.md`.
- Accion: documentar columna target, clases, distribucion y posible desbalance.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: con apoyo en documentacion.
- Dependencias: T-1.1.
- Criterio de verificacion: target aceptado por el equipo y distribucion documentada.
- Evidencia: target `booking_status`, clases `Not_Canceled` (67,24%) y `Canceled` (32,76%), documentado en `.specify/2_spec.md`, `reports/data_dictionary.md` y notebooks de EDA.
- Comando de verificacion: revisar `notebooks/01_dataset_inspection.ipynb` y `notebooks/02_eda_exploratory.ipynb`.

### [x] T-1.3 Crear diccionario de datos

- Archivos afectados: `reports/`, `README.md`.
- Accion: listar columnas, tipo de dato, descripcion, rol y si entra al modelo.
- Responsable sugerido: I4 con revision de I1.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: T-1.1.
- Criterio de verificacion: todas las columnas relevantes estan clasificadas.
- Evidencia: diccionario inicial creado en `reports/data_dictionary.md`.
- Comando de verificacion: no aplica.

### [x] T-1.4 Realizar EDA inicial

- Archivos afectados: `notebooks/`, `reports/figures/`, `reports/model_report.md`.
- Accion: analizar nulos, duplicados, distribuciones, target, correlaciones y relaciones con target.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-1.1, T-1.2.
- Criterio de verificacion: existen graficos relevantes para clasificacion.
- Evidencia: `notebooks/02_eda_exploratory.ipynb` incluye revision de nulos, duplicados, target, distribuciones numericas, variables categoricas, relacion con target, correlaciones, interpretaciones y conclusiones finales.
- Comando de verificacion: `rg -n "TODO|a completar" notebooks/02_eda_exploratory.ipynb`.

### [x] T-1.5 Interpretar graficos para negocio

- Archivos afectados: `reports/model_report.md`, `docs/business_presentation/`.
- Accion: escribir interpretaciones simples de los graficos principales.
- Responsable sugerido: I4 con revision de I1.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: T-1.4.
- Criterio de verificacion: cada grafico usado en presentacion tiene una lectura clara.
- Avance: interpretaciones tecnicas agregadas en `notebooks/02_eda_exploratory.ipynb`.
- Evidencia: lecturas principales trasladadas a `docs/business_presentation/eda_business_insights.md`.
- Comando de verificacion: no aplica.

## Fase 2 - Nivel Esencial MVP

### [x] T-2.1 Crear pipeline de preprocesamiento

- Archivos afectados: `src/features/`, `src/models/`, `tests/unit/`, `requirements.txt`.
- Accion: construir transformaciones para numericas, categoricas y columnas excluidas.
- Responsable sugerido: I1.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-1.2, T-1.3, T-1.4.
- Criterio de verificacion: el pipeline transforma train y validacion sin errores ni leakage.
- Evidencia: `src/features/preprocessing.py` define columnas, target, exclusion de `Booking_ID`, split estratificado y `ColumnTransformer`.
- Comando de verificacion: `python -m unittest tests.unit.test_preprocessing`.

### [x] T-2.2 Entrenar baseline

- Archivos afectados: `src/models/`, `models/`, `reports/model_report.md`.
- Accion: entrenar modelo simple y guardar metricas train-validacion, usando F1-score de la clase `Canceled` como metrica principal.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-2.1.
- Criterio de verificacion: baseline registrado en tabla de experimentos.
- Evidencia: `src/models/train_baseline.py` entrena `dummy_most_frequent` y `logistic_regression_balanced`; el modelo real queda guardado en `models/baseline/logistic_regression_baseline.pkl`.
- Comando de verificacion: `python -m src.models.train_baseline` y `python -m unittest discover`.

### [x] T-2.3 Calcular metricas obligatorias

- Archivos afectados: `src/evaluation/`, `reports/model_report.md`, `reports/figures/`.
- Accion: calcular F1-score de la clase `Canceled` como metrica principal, junto con accuracy, precision, recall, ROC-AUC, matriz de confusion y curva ROC si aplica.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: con apoyo para documentar resultados.
- Dependencias: T-2.2.
- Criterio de verificacion: metricas visibles en informe.
- Evidencia: `reports/model_report.md` incluye accuracy, precision, recall, F1, ROC-AUC, conteos de matriz de confusion, feature importance equivalente y analisis de errores; `reports/figures/` incluye matriz de confusion y curva ROC.
- Comando de verificacion: `python -m src.models.train_baseline`, `python -m src.evaluation.model_diagnostics` y `python -m pytest`.

### [x] T-2.4 Revisar overfitting inferior al 5%

- Archivos afectados: `reports/model_report.md`, tabla de experimentos.
- Accion: comparar F1-score de la clase `Canceled` en train y validacion.
- Responsable sugerido: I1 con QA de I4.
- Dificultad: media.
- Apto junior: si para checklist, no para decision tecnica final.
- Dependencias: T-2.3.
- Criterio de verificacion: diferencia < 0.05 o bloqueo documentado.
- Evidencia: `reports/model_report.md` documenta F1 train 0,6949, F1 validacion 0,6870 y gap 0,0079 para Logistic Regression.
- Comando de verificacion: revisar seccion "Revision inicial de overfitting" en `reports/model_report.md` y ejecutar `python -m unittest discover`.

### [x] T-2.5 Crear app minima de prediccion

- Archivos afectados: `app/`, `README.md`.
- Accion: crear formulario, cargar modelo y devolver prediccion.
- Responsable sugerido: I2.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-2.2.
- Criterio de verificacion: usuario puede ingresar datos y obtener clase predicha.
- Evidencia: `POST /predict` carga el Champion Random Forest guardado en `models/champion/random_forest_champion.pkl`; `GET /model/info` devuelve `random_forest_champion_v0.1.0`.
- Evidencia frontend: la tabla de reservas, las alertas y el modal consumen reservas reales desde `GET /reservations/demo` y predicciones reales desde `POST /predict`.
- Comando de verificacion: `python -m pytest tests/test_backend_api.py`.
- Nota de estado: app frontend y backend FastAPI tienen contrato real de inferencia con el Champion. La validacion manual funcional queda cerrada en T-2.6 y documentada en `reports/manual_app_validation.md`.

### [x] T-2.6 Validacion manual de app

- Archivos afectados: `docs/`, `reports/`, `README.md`.
- Accion: probar 5 entradas manuales, tomar capturas y registrar resultados.
- Responsable sugerido: I4.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: T-2.5.
- Criterio de verificacion: capturas y checklist de validacion completos.
- Evidencia: validacion funcional documentada en `reports/manual_app_validation.md`.
- Comando de verificacion: no aplica.

## Fase 3 - Nivel Medio

### [x] T-3.1 Entrenar modelo ensemble

- Archivos afectados: `src/models/`, `models/`, `reports/model_report.md`.
- Accion: entrenar Random Forest, Gradient Boosting u otro ensemble justificado.
- Responsable sugerido: I1.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-2.1, T-2.3.
- Criterio de verificacion: ensemble comparado contra baseline.
- Evidencia: `src/models/train_challengers.py` entrena `random_forest_challenger` y lo compara contra `dummy_most_frequent` y `logistic_regression_balanced`; el artefacto queda en `models/challengers/random_forest_challenger.pkl`.
- Resultado clave: F1 validacion clase `Canceled` mejora de 0,6870 en Logistic Regression a 0,8042 en Random Forest optimizado.
- Comando de verificacion: `python -m src.models.train_challengers`.

### [x] T-3.2 Aplicar validacion cruzada

- Archivos afectados: `src/models/`, `reports/model_report.md`.
- Accion: ejecutar K-Fold o estrategia equivalente y reportar promedio/desviacion.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-3.1.
- Criterio de verificacion: resultados de CV documentados.
- Evidencia: `reports/model_report.md` incluye validacion cruzada estratificada de 3 folds para `random_forest_challenger`.
- Resultado clave: F1 CV medio 0,8082 con desviacion 0,0053; ROC-AUC CV medio 0,9391 con desviacion 0,0015.
- Comando de verificacion: `python -m src.models.train_challengers`.

### [x] T-3.3 Optimizar hiperparametros

- Archivos afectados: `src/models/`, `reports/model_report.md`.
- Accion: usar GridSearch, RandomSearch u Optuna si se justifica.
- Responsable sugerido: I1.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-3.2.
- Criterio de verificacion: mejores parametros y comparacion documentados.
- Evidencia: la configuracion optimizada esta aplicada en `src/models/train_challengers.py`, el artefacto fue regenerado en `models/challengers/random_forest_challenger.pkl` y el resultado esta documentado en `reports/model_report.md`.
- Mejor configuracion: `n_estimators=200`, `max_depth=18`, `min_samples_leaf=6`, `min_samples_split=12`, `class_weight="balanced_subsample"`.
- Resultado: F1 validacion 0,8105, gap train-validacion 0,0345 y ROC-AUC validacion 0,9391.
- Verificacion automatizada: `tests/unit/test_challenger_training.py` comprueba hiperparametros, F1 minimo y regla de overfitting.
- Comando de verificacion: `python -m pytest tests/unit/test_challenger_training.py`.

### [x] T-3.4 Seleccionar Champion Model

- Archivos afectados: `models/champion/`, `reports/model_report.md`, `.specify/2_spec.md`.
- Accion: elegir modelo final segun metricas, overfitting, estabilidad e integracion con app.
- Responsable sugerido: I1 con revision de I2 e I3.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-3.3, T-2.5.
- Criterio de verificacion: Champion versionado y explicado.
- Evidencia: Random Forest queda promocionado como Champion en `models/champion/random_forest_champion.pkl`, con metadata en `models/champion/champion_metadata.json` y API FastAPI cargandolo desde `app/backend/services/model_service.py`.
- Resultado clave: `GET /model/info` devuelve `random_forest_champion_v0.1.0` y `RandomForestClassifier`.
- Evaluacion final: holdout ejecutado una unica vez sobre 5442 filas; F1 `Canceled` 0,8258, ROC-AUC 0,9499 y gap validacion-test 0,0153.
- Evidencia final: `docs/champion_holdout_protocol.md`, `reports/champion_test_metrics.json` y metadata Champion actualizada.
- Comando de verificacion: `python -m pytest tests/test_backend_api.py` y `python -m pytest`.

### [x] T-3.5 Crear tabla de experimentos

- Archivos afectados: `reports/`, `README.md`.
- Accion: registrar modelo, parametros, metricas train/validacion, overfitting y decision.
- Responsable sugerido: I4 con revision de I1.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: T-2.2.
- Criterio de verificacion: todos los modelos probados aparecen en la tabla.
- Evidencia: tabla de experimentos y decision incluida en `reports/model_report.md`; tabla completa de tuning disponible en `reports/random_forest_tuning_results.csv`.
- Comando de verificacion: no aplica.

### [x] T-3.6 Implementar feedback

- Archivos afectados: `app/`, `data/feedback/`, `src/data/`.
- Accion: guardar feedback de usuario y predicciones para futuro reentrenamiento.
- Responsable sugerido: I2.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-2.5.
- Criterio de verificacion: feedback queda persistido y se puede abrir.
- Evidencia: `POST /feedback` guarda prediccion, probabilidad, version de modelo, input validado, feedback de usuario y estado real mediante la capa SQLAlchemy.
- Evidencia adicional: `GET /feedback/summary` devuelve el numero de registros persistidos y el backend de almacenamiento sin exponer credenciales.
- Evidencia de gestion: `GET /feedback` devuelve el historico y `PATCH /feedback/{record_id}` permite corregir el resultado real y los comentarios.
- Evidencia frontend: el modal de detalle del frontend principal registra feedback mediante `POST /feedback`.
- Evidencia operativa: SQLite se usa por defecto en local y PostgreSQL en Amazon RDS en el despliegue AWS.
- Comando de verificacion: `python -m pytest tests/test_backend_api.py`.

## Fase 4 - Nivel Avanzado

### [x] T-4.1 Crear tests minimos de preprocessing

- Archivos afectados: `tests/`, `src/features/`.
- Accion: validar que el pipeline procesa datos validos y rechaza datos invalidos controlados.
- Responsable sugerido: I3.
- Dificultad: media.
- Apto junior: con guia para casos simples.
- Dependencias: T-2.1.
- Criterio de verificacion: tests pasan.
- Evidencia: `tests/unit/test_preprocessing.py` verifica el contrato de features y target, el split estratificado, la transformacion sin valores `NaN` y el rechazo controlado de columnas obligatorias ausentes y clases target desconocidas.
- Comando de verificacion: `python -m pytest`

### [x] T-4.2 Crear tests minimos de metricas

- Archivos afectados: `tests/`, `src/evaluation/`.
- Accion: testear umbral minimo y regla de overfitting.
- Responsable sugerido: I3.
- Dificultad: media.
- Apto junior: con guia.
- Dependencias: T-2.3, T-2.4.
- Criterio de verificacion: tests pasan y fallan si la regla se incumple.
- Evidencia: `tests/unit/test_baseline_training.py` y `tests/unit/test_challenger_training.py` verifican metricas minimas, versionado, parametros del challenger y regla de overfitting.
- Evidencia CI: `.github/workflows/backend-tests.yml` ejecuta la suite Python completa y se reutiliza como quality gate del despliegue.
- Comando de verificacion: `python -m pytest`

### [x] T-4.3 Dockerizar app

- Archivos afectados: `Dockerfile`, `docker-compose.yml`, `README.md`.
- Accion: crear imagen que levante la app y cargue el modelo Champion.
- Responsable sugerido: I3.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-2.5, T-3.4.
- Criterio de verificacion: app levanta con Docker.
- Comando de verificacion: `docker compose build`, `docker compose up -d`, `GET /health/ready`, `GET /model/info`, `POST /predict`, `POST /feedback`, `GET /feedback`, `PATCH /feedback/{record_id}`, `GET /feedback/summary`, `GET /monitoring/drift`, `curl.exe -I http://localhost:8080/` y `docker compose down`.
- Evidencia: Docker validado con frontend nginx, backend FastAPI, Champion Random Forest, esquema migrado, feedback y monitorizacion de drift.
- Resultado clave: Docker devuelve `random_forest_champion_v0.1.0`, prediccion correcta, feedback persistido y frontend `HTTP/1.1 200 OK`.
- Evidencia adicional: Docker incluye `data/raw/` en la imagen backend para servir `GET /reservations/demo` y permitir que el frontend principal use reservas reales.

### [x] T-4.4 Conectar almacenamiento persistente

- Archivos afectados: `app/`, `src/data/`, `data/feedback/`.
- Accion: usar CSV, SQLite o base de datos para predicciones y feedback.
- Responsable sugerido: I2 con apoyo de I3.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-3.6.
- Criterio de verificacion: datos persisten tras reiniciar app.
- Evidencia: capa SQLAlchemy con SQLite local en `data/app/hotel_insights.db` y PostgreSQL en Amazon RDS para el despliegue AWS.
- Evidencia adicional: `src/data/feedback_ingestion.py` consulta registros etiquetados con `actual_status` y genera un dataset compatible con el pipeline para futuros reentrenamientos.
- Evidencia de persistencia: `GET /feedback/summary` mantiene el contador tras reiniciar el backend desplegado y devuelve `storage: postgresql`.
- Comando de verificacion: `python -m pytest tests/unit/test_feedback_ingestion.py`.

### [x] T-4.5 Documentar instalacion y ejecucion

- Archivos afectados: `README.md`, `docs/project_management/`.
- Accion: escribir pasos para entorno local, app, tests y Docker.
- Responsable sugerido: I4 con revision de I2 e I3.
- Evidencia de reproducibilidad: `requirements.txt` y `requirements-backend.txt` fijan versiones exactas para desarrollo, CI y la imagen de produccion.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: T-2.5, T-4.3.
- Criterio de verificacion: otra persona puede seguir el README.
- Comando de verificacion: ejecutar comandos documentados y revisar `docs/aws_deployment.md`.
- Evidencia: README actualizado para local y Docker; `docs/aws_deployment.md` documenta arquitectura, configuracion, despliegue manual y automatico, seguridad, verificacion y retirada de AWS.

### [x] T-4.6 Desplegar app y automatizar entrega

- Archivos afectados: `docker-compose.ec2.yml`, `.github/workflows/deploy-aws-ec2.yml`, `scripts/deploy_ec2.sh`, `docs/aws_deployment.md`.
- Accion: desplegar la aplicacion web y automatizar la publicacion de releases desde `main`.
- Responsable sugerido: I3 con revision de I2 e I4.
- Dificultad: alta.
- Apto junior: no como responsable unico.
- Dependencias: T-4.3, T-4.4, T-4.5.
- Criterio de verificacion: URL HTTPS publica disponible, Champion cargado, PostgreSQL operativo y despliegue automatico verificado.
- Evidencia: CloudFront publica la app; EC2 ejecuta Docker Compose; RDS PostgreSQL persiste feedback; GitHub Actions despliega mediante OIDC y SSM tras cada merge en `develop`.
- Evidencia de quality gate: el job de despliegue depende de la suite Python completa y del build frontend mediante `needs`.
- Política de release: `develop` integra el trabajo del equipo y `main` es la única rama que activa el despliegue de producción.
- Evidencia de seguridad: RDS es privado y el puerto HTTP de EC2 solo admite trafico desde la lista administrada de CloudFront.
- URL verificada: `https://d3lxpalnzir74p.cloudfront.net`.

### [x] T-4.7 Versionar el esquema de base de datos

- Archivos afectados: `alembic/`, `alembic.ini`, `src/data/`, `app/backend/Dockerfile`, `scripts/start_backend.sh`, `tests/`, `docs/`.
- Accion: sustituir la creacion implicita de tablas por migraciones Alembic reproducibles.
- Responsable sugerido: I3.
- Dificultad: alta.
- Apto junior: no como responsable unico.
- Dependencias: T-4.4, T-4.6.
- Criterio de verificacion: SQLite y PostgreSQL alcanzan la revision `0002_prediction_logs` sin perder registros existentes.
- Evidencia: migracion inicial compatible con bases nuevas y con la tabla historica creada antes de Alembic; un esquema incompatible detiene el despliegue.
- Evidencia operativa: `scripts/start_backend.sh` ejecuta `alembic upgrade head` antes de iniciar FastAPI en Docker local y AWS.
- Tests: `tests/unit/test_database_migrations.py` cubre creacion, adopcion sin perdida y rechazo de schema incompatible.
- Comando de verificacion: `python -m pytest tests/unit/test_database_migrations.py` y `python -m alembic current`.

### [x] T-4.8 Auditar todas las predicciones

- Archivos afectados: `app/backend/`, `src/data/models.py`, `alembic/versions/`, `tests/`, `docs/`.
- Accion: persistir cada respuesta correcta de `POST /predict` con identificador unico, input, resultado y version de modelo.
- Responsable sugerido: I3.
- Dificultad: media.
- Dependencias: T-2.5, T-4.4, T-4.7.
- Criterio de verificacion: una respuesta `200 OK` incluye `prediction_id` y existe un registro equivalente en `prediction_logs`.
- Evidencia: `prediction_log_service.py` confirma la transaccion antes de devolver la respuesta; un fallo de persistencia impide una prediccion correcta sin auditar.
- Migracion: `0002_prediction_logs` crea la tabla e indices por fecha y version de modelo.
- Tests: contrato de API, persistencia del payload y ciclo de migracion.
- Comando de verificacion: `python -m pytest tests/test_backend_api.py tests/unit/test_database_migrations.py`.

### [x] T-4.9 Anadir observabilidad operativa

- Archivos afectados: `app/backend/`, `docker-compose.yml`, `docker-compose.ec2.yml`, `scripts/`, `.gitattributes`, `tests/`, `docs/`.
- Accion: separar liveness y readiness, emitir logs JSON y correlacionar solicitudes e inferencias sin registrar datos sensibles.
- Responsable sugerido: I3.
- Dificultad: media.
- Dependencias: T-4.6, T-4.7, T-4.8.
- Criterio de verificacion: `GET /health/ready` solo responde `200` con Champion y esquema operativo migrado; todas las respuestas incluyen `X-Request-ID`.
- Evidencia: Docker y el despliegue AWS esperan el readiness check; `prediction_completed` relaciona `request_id`, `prediction_id` y version del modelo.
- Privacidad: los logs no incluyen payloads de reserva, credenciales ni cadenas de conexion.
- Documentacion: `docs/observability.md`, `docs/api_contract.md` y `docs/aws_deployment.md`.
- Comando de verificacion: `python -m pytest tests/test_backend_api.py tests/unit/test_observability.py tests/integration/test_prediction_feedback_smoke.py`.

## Fase 5 - Nivel Experto

### [x] T-5.1 Entrenar red neuronal experimental

- Archivos afectados: `src/models/`, `models/challengers/`, `reports/model_report.md`.
- Accion: entrenar red neuronal comparable contra Champion.
- Responsable sugerido: I3 con apoyo de I1.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-3.4.
- Criterio de verificacion: metricas comparables documentadas.
- Evidencia: `src/models/train_neural_network.py`, `models/challengers/mlp_neural_network_challenger.pkl` y `reports/neural_network_experiment.json`. El MLP obtiene F1 de validacion `0.7742`, gap `0.0416` y no mejora el Champion.
- Estado actual: completada como experimento comparable; decision `retain_champion`.
- Comando de verificacion: `python -m pytest tests/unit/test_neural_network_experiment.py`.

### [x] T-5.2 Implementar o simular A/B Testing

- Archivos afectados: `src/mlops/`, `app/`, `reports/model_report.md`.
- Accion: enrutar o simular trafico entre Champion y Challenger registrando `model_version`.
- Responsable sugerido: I3.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-3.4, T-5.1.
- Criterio de verificacion: comparacion Champion vs Challenger reproducible.
- Evidencia: `src/mlops/offline_ab_test.py`, `reports/offline_ab_test_results.json` y `reports/offline_ab_test_assignments.csv`. La simulacion offline estratificada 80/20 obtiene F1 `0.8113` para Champion y `0.7858` para MLP, con intervalo bootstrap `[-0.0620, 0.0135]`.
- Estado actual: completada; no existe victoria estadisticamente respaldada del Challenger y se conserva el Champion.
- Comando de verificacion: `python -m pytest tests/unit/test_offline_ab_testing.py`.

### [x] T-5.3 Medir Data Drift

- Archivos afectados: `src/mlops/`, `models/monitoring/`, `app/backend/`, `tests/`, `docs/`.
- Accion: calcular PSI entre el perfil congelado de entrenamiento y las predicciones operativas persistidas en `prediction_logs`.
- Responsable sugerido: I3.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-3.6.
- Criterio de verificacion: reporte de drift con umbrales.
- Evidencia: `models/monitoring/training_reference_profile.json` contiene el perfil versionado del split de entrenamiento, `GET /monitoring/drift` analiza las 1.000 predicciones operativas mas recientes cuando existen al menos 100 registros validos y `/monitoring` presenta el estado en un dashboard interno independiente.
- Control de muestra: `X-Prediction-Source` distingue llamadas `api`, evaluaciones `frontend_manual` y calculos historicos `frontend_demo_queue`; la cola demo y el origen heredado `prediction_api` se conservan en auditoria pero se excluyen del PSI.
- Umbrales: PSI menor de 0.10 estable; entre 0.10 y 0.25 aviso; desde 0.25 drift alto.
- Comportamiento seguro: con menos de 100 registros devuelve `insufficient_data` y nunca promociona modelos automaticamente.
- Tests: casos de muestra insuficiente, distribucion estable, drift alto, transformacion de predicciones, filtrado por origen, limite de muestra reciente y contrato API.
- Documentacion: `docs/data_drift_monitoring.md` y `docs/api_contract.md`.
- Contrato frontend: `tests/unit/test_monitoring_frontend_entry.py` protege la entrada Vite, la ruta nginx y su inclusion en la imagen Docker.
- Estado actual: implementacion tecnica completa. La acumulacion de 100 predicciones operativas reales es una condicion de ejecucion para obtener un resultado concluyente, no una tarea de desarrollo pendiente.
- Comando de verificacion: `python -m pytest tests/unit/test_data_drift.py tests/unit/test_prediction_ingestion.py tests/unit/test_monitoring_frontend_entry.py tests/test_backend_api.py`.

### [x] T-5.4 Auto-reemplazo condicionado

- Archivos afectados: `src/mlops/`, `models/`, `reports/model_report.md`.
- Accion: crear logica que promueva un Challenger solo si supera reglas de metricas y overfitting.
- Responsable sugerido: I3 con revision de I1.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-5.2, T-5.3.
- Criterio de verificacion: un modelo inferior no reemplaza al Champion en prueba controlada.
- Evidencia: `src/mlops/conditional_promotion.py` y `reports/conditional_promotion_decision.json`. La politica exige mejora F1 `+0.02`, gap inferior a `0.05`, degradacion critica maxima `0.02`, evidencia A/B positiva y artefacto compatible.
- Seguridad: Data Drift nunca promociona modelos; la aplicacion requiere `--apply`, crea backup y el MLP actual es rechazado por tres gates.
- Estado actual: completada como promocion controlada; un modelo inferior no sustituye al Champion.
- Comando de verificacion: `python -m pytest tests/unit/test_conditional_promotion.py`.

### [x] T-5.5 Documentar ciclo MLOps para defensa

- Archivos afectados: `docs/technical_presentation/`, `reports/model_report.md`.
- Accion: explicar Champion/Challenger, A/B, drift y auto-reemplazo con diagrama simple.
- Responsable sugerido: I4 con revision de I3.
- Dificultad: media.
- Apto junior: si con plantilla.
- Dependencias: T-5.2, T-5.3, T-5.4.
- Criterio de verificacion: la presentacion explica reglas y limitaciones sin prometer mas de lo implementado.
- Evidencia: `reports/model_report.md`, `docs/data_drift_monitoring.md`, `docs/technical_presentation/model_metrics_review.md`, `GET /monitoring/experiments` y dashboard `/monitoring`.
- Estado actual: completada con resultados reales, reglas, decisiones y limitaciones del ciclo Champion/Challenger.
- Comando de verificacion: `python -m pytest tests/unit/test_monitoring_frontend_entry.py tests/test_backend_api.py`.

## Fase 6 - Cierre

### [x] T-6.1 Smoke test completo

- Archivos afectados: `reports/`, `README.md`.
- Accion: ejecutar app, cargar modelo, hacer prediccion, guardar feedback y revisar salida.
- Responsable sugerido: I2 e I4.
- Dificultad: baja.
- Apto junior: si para validacion manual.
- Dependencias: T-2.5, T-3.6.
- Criterio de verificacion: checklist de demo completo.
- Evidencia: `tests/integration/test_prediction_feedback_smoke.py` valida flujo completo de API con health, metadata de modelo, prediccion, feedback y resumen de feedback.
- Evidencia Docker: flujo validado manualmente con `docker compose build`, `docker compose up -d`, endpoints backend y frontend nginx.
- Evidencia frontend: `pnpm build` valida el frontend principal conectado al servicio real de prediccion y reservas.
- Evidencia final de producto: la navegación definitiva incluye portada, operación, evaluación, feedback y explicación del modelo; sus cifras se contrastaron con el CSV y los artefactos finales.
- Comando de verificacion: `python -m pytest tests/integration/test_prediction_feedback_smoke.py`.

### [x] T-6.2 Revision final de overfitting y metricas

- Archivos afectados: `reports/model_report.md`, `docs/technical_presentation/`.
- Accion: revisar que metricas finales coincidan con informe, README y presentacion.
- Responsable sugerido: I1 con QA de I4.
- Dificultad: media.
- Apto junior: si para checklist, no para decision tecnica.
- Dependencias: T-3.4.
- Criterio de verificacion: overfitting < 5% demostrado y sin contradicciones.
- Evidencia: `docs/technical_presentation/model_metrics_review.md` alinea modelo, version, F1, validacion cruzada y gap de overfitting con `reports/model_report.md`, README y artefactos Champion.
- Resultado: gap F1 del Champion `0.0345`, inferior al limite `0.05`.
- Comando de verificacion: `python -m pytest tests/unit/test_challenger_training.py`.

### [ ] T-6.3 Preparar presentacion de negocio

- Archivos afectados: `docs/business_presentation/`.
- Accion: preparar narrativa, problema, solucion, demo, impacto y limitaciones.
- Responsable sugerido: I4 con apoyo de todo el equipo.
- Dificultad: media.
- Apto junior: si.
- Dependencias: T-1.5, T-2.6.
- Criterio de verificacion: presentacion no contiene tecnicismos innecesarios y usa capturas reales.
- Comando de verificacion: no aplica.

### [ ] T-6.4 Preparar presentacion tecnica

- Archivos afectados: `docs/technical_presentation/`.
- Accion: explicar estructura, preprocessing, modelos, metricas, app, Docker y MLOps si aplica.
- Responsable sugerido: I1, I2 e I3, coordinado por I4.
- Dificultad: media.
- Apto junior: si como coordinacion y formato.
- Dependencias: T-3.4, T-4.3, T-5.5.
- Criterio de verificacion: cada decision tecnica importante tiene evidencia.
- Comando de verificacion: no aplica.

### [ ] T-6.5 Checklist final de consigna

- Archivos afectados: `README.md`, `reports/`, `.specify/4_tasks.md`.
- Accion: revisar app, GitHub, informe, presentaciones, Jira, Docker, tests y niveles alcanzados.
- Responsable sugerido: I4 con revision de todo el equipo.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: todas las tareas de cierre.
- Criterio de verificacion: no quedan requisitos obligatorios sin evidencia.
- Evidencia tecnica cerrada: release de `develop` a `main`, quality gates, despliegue AWS y smoke test publico completados sobre `ac68ca1`.
- Pendiente de equipo: confirmar presentaciones finales y alineacion de Jira antes de marcar la tarea completa.
- Comando de verificacion: no aplica.
