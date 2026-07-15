# SPEC 2 - Technical Specification

Este archivo es la Single Source of Truth del proyecto. Toda implementacion debe respetar este contrato o actualizarlo de forma explicita antes de cambiar el alcance.

## Estado actual

- Repositorio: `proyecto5-grupo2`.
- README inicial: actualizado con descripcion del proyecto, estructura, ejecucion del frontend, metodologia SPEC, flujo Git, roles y roadmap.
- Dataset: Hotel Reservations Classification Dataset.
- Archivo incorporado: `data/raw/hotel-reservations-classification-dataset/Hotel Reservations.csv`.
- Fuente de referencia: Kaggle, kernel `marawaneslam/hotel-reservations-classification`.
- Ruta original en Kaggle: `/kaggle/input/hotel-reservations-classification-dataset/Hotel Reservations.csv`.
- Cliente del proyecto: plataforma de reservas hoteleras tipo Booking, Trivago o Agoda.
- Problema de negocio: predecir si una reserva sera cancelada.
- Target: `booking_status`.
- Metrica principal: F1-score de la clase `Canceled`.
- Metricas secundarias: precision, recall, ROC-AUC y matriz de confusion.
- Tecnologia de app: frontend web con React + Vite y backend de inferencia con FastAPI.
- Sistema de gestion: Jira.
- Tablero Jira: `https://miguel-redondo.atlassian.net/jira/software/projects/G2PC/boards/100/backlog`.
- Frontend actual: existe en `app/frontend` con tabla, alertas, modal, formulario y feedback conectados al backend real.
- Backend actual: existe API FastAPI en `app/backend` con `GET /health`, `GET /health/ready`, `GET /model/info`, `GET /reservations/demo`, `POST /predict`, `POST /feedback`, `GET /feedback/summary`, `GET /feedback`, `PATCH /feedback/{record_id}` y `GET /monitoring/drift`.
- Contrato API actual: `docs/api_contract.md`.
- Documentacion de organizacion: existe en `docs/project_management/`.

## Tipo de problema

- Tipo: clasificacion supervisada binaria.
- Entrada: variables tabulares del dataset elegido.
- Salida: estado de la reserva predicho.
- Salida opcional: probabilidad o confianza de la prediccion si el modelo lo permite.

## Dataset

Dataset definitivo: Hotel Reservations Classification Dataset.

Archivo de trabajo:

```text
data/raw/hotel-reservations-classification-dataset/Hotel Reservations.csv
```

Estado del archivo:

- CSV incorporado en el repositorio.
- Filas: 36.275.
- Columnas: 19.

Fuente de referencia:

- Kaggle kernel: `marawaneslam/hotel-reservations-classification`.
- Comando de referencia del kernel: `kaggle kernels pull marawaneslam/hotel-reservations-classification`.
- Ruta usada en Kaggle: `/kaggle/input/hotel-reservations-classification-dataset/Hotel Reservations.csv`.

CSV incorporado en `data/raw/hotel-reservations-classification-dataset/Hotel Reservations.csv`.

Validacion inicial:

- Filas: 36.275.
- Columnas: 19.
- Valores nulos: 0.
- Duplicados exactos: 0.
- Notebook de inspeccion: `notebooks/01_dataset_inspection.ipynb`.
- Notebook de EDA: `notebooks/02_eda_exploratory.ipynb`.
- Diccionario de datos: `reports/data_dictionary.md`.

### Criterios para elegir dataset

El dataset debe cumplir:

- Tener una variable objetivo categorica clara.
- Tener suficientes filas para separar train, validacion y test.
- Permitir EDA con visualizaciones relevantes.
- Tener variables explicativas interpretables.
- No depender de datos sensibles que no puedan usarse en una app.
- Tener licencia o fuente aceptable para uso academico.
- Permitir una historia de negocio o decision clara.
- Evitar leakage evidente entre features y target.
- Tener una distribucion de clases que pueda evaluarse con metricas de clasificacion.

### Variable objetivo

Target definitivo: `booking_status`.

Debe documentarse:

- Nombre de columna: `booking_status`.
- Clases esperadas: `Canceled` y `Not_Canceled`.
- Distribucion de clases:
  - `Not_Canceled`: 24.390 registros, 67,24%.
  - `Canceled`: 11.885 registros, 32,76%.
- Desbalance: moderado. La clase mayoritaria es `Not_Canceled`, por lo que se recomienda vigilar precision, recall y F1, no solo accuracy.
- Si se requiere binarizacion o agrupacion: no se requiere agrupacion; para modelos se codificara como variable binaria.
- Justificacion: es una variable categorica que indica el resultado historico de la reserva, por lo que permite entrenar un modelo de clasificacion supervisada.

### Features esperadas

Features candidatas iniciales:

- `no_of_adults`.
- `no_of_children`.
- `no_of_weekend_nights`.
- `no_of_week_nights`.
- `type_of_meal_plan`.
- `required_car_parking_space`.
- `room_type_reserved`.
- `lead_time`.
- `arrival_year`.
- `arrival_month`.
- `arrival_date`.
- `market_segment_type`.
- `repeated_guest`.
- `no_of_previous_cancellations`.
- `no_of_previous_bookings_not_canceled`.
- `avg_price_per_room`.
- `no_of_special_requests`.

Columna candidata a excluir:

- `Booking_ID`: identificador de reserva sin valor predictivo generalizable.

Columnas confirmadas despues de cargar el CSV:

- Numericas: `no_of_adults`, `no_of_children`, `no_of_weekend_nights`, `no_of_week_nights`, `lead_time`, `arrival_year`, `arrival_month`, `arrival_date`, `no_of_previous_cancellations`, `no_of_previous_bookings_not_canceled`, `avg_price_per_room`, `no_of_special_requests`.
- Categoricas nominales: `type_of_meal_plan`, `room_type_reserved`, `market_segment_type`.
- Binarias: `required_car_parking_space`, `repeated_guest`.
- Target: `booking_status`.
- Excluida: `Booking_ID`.

No se detectaron columnas posteriores al evento que generen leakage evidente en esta revision inicial.

La seleccion de features debe clasificar columnas en:

- Numericas.
- Categoricas nominales.
- Categoricas ordinales.
- Booleanas.
- Fechas o variables temporales.
- Columnas a excluir.

Columnas a excluir siempre:

- Identificadores sin valor predictivo.
- Columnas posteriores al evento que generen leakage.
- Duplicados exactos.
- Variables con informacion directa del target.
- Datos sensibles no necesarios para la prediccion.

## Estado del EDA exploratorio

EDA inicial documentado en `notebooks/02_eda_exploratory.ipynb`.

Hallazgos principales:

- Dataset completo a nivel de nulos y sin duplicados exactos.
- Target binario con desbalance moderado.
- `lead_time` muestra una relacion fuerte con cancelacion: las reservas canceladas tienen mayor anticipacion media y mediana que las no canceladas.
- `avg_price_per_room` tambien tiende a ser mayor en reservas canceladas, aunque con una diferencia menos marcada.
- `no_of_special_requests` muestra relacion inversa con cancelacion: las reservas con mas solicitudes especiales tienden a cancelarse menos.
- `market_segment_type` y `repeated_guest` muestran diferencias relevantes en tasa de cancelacion.
- Hay variables con asimetria y rangos amplios, especialmente `lead_time`, `avg_price_per_room` y variables historicas con muchos ceros.

Implicaciones para preprocessing:

- Excluir `Booking_ID` antes del entrenamiento.
- Separar train, validacion y test de forma estratificada.
- Ajustar transformaciones solo con train para evitar leakage.
- Usar One-Hot Encoding para categoricas con `handle_unknown='ignore'`.
- Mantener variables binarias como 0/1.
- Escalar numericas si el baseline usa Logistic Regression u otro modelo sensible a escala.
- Comparar el baseline contra un `DummyClassifier` de clase mayoritaria.

## Estado del preprocessing inicial

Pipeline inicial implementado en `src/features/preprocessing.py`.

Contrato implementado:

- Carga del CSV crudo desde `data/raw/hotel-reservations-classification-dataset/Hotel Reservations.csv`.
- Validacion de columnas requeridas antes de preparar datos.
- Separacion de `X` e `y`.
- Exclusion de `Booking_ID` antes de entrenar.
- Codificacion del target: `Not_Canceled` = 0 y `Canceled` = 1.
- Split estratificado train/validacion/test con proporcion 70% / 15% / 15%.
- `ColumnTransformer` con:
  - `StandardScaler` para variables numericas.
  - `OneHotEncoder(handle_unknown="ignore")` para categoricas.
  - `passthrough` para binarias.

Verificacion actual:

- Pruebas unitarias en `tests/unit/test_preprocessing.py`.
- Comando: `python -m unittest tests.unit.test_preprocessing`.
- Estado: el preprocessing transforma train y validacion sin errores y mantiene la distribucion del target en los splits.

## Estado del baseline inicial

Baseline reproducible implementado en `src/models/train_baseline.py`.

Modelos evaluados:

- `dummy_most_frequent`: referencia minima que siempre predice la clase mayoritaria.
- `logistic_regression_balanced`: primer modelo real con el pipeline de preprocessing y pesos balanceados para el target.

Resultados de validacion:

- DummyClassifier: F1-score clase `Canceled` = 0,0000; ROC-AUC = 0,5000.
- Logistic Regression: F1-score clase `Canceled` = 0,6870; ROC-AUC = 0,8604.
- Gap train-validacion en F1 de Logistic Regression: 0,0079.
- Resultado de overfitting: cumple la regla de diferencia inferior a 0,05.

Evidencia:

- Reporte tecnico: `reports/model_report.md`.
- Modelo guardado: `models/baseline/logistic_regression_baseline.pkl`.
- Matriz de confusion: `reports/figures/baseline_logistic_confusion_matrix.png`.
- Curva ROC: `reports/figures/baseline_logistic_roc_curve.png`.
- Comando: `python -m src.models.train_baseline`.
- Pruebas automaticas: `tests/unit/test_baseline_training.py`.
- Comando de pruebas: `python -m unittest discover`.

Decision actual:

- Logistic Regression queda como baseline inicial, no como Champion definitivo.
- El test final queda reservado para evaluar candidatos posteriores de forma mas imparcial.

## Estado del ensemble challenger

Challenger reproducible implementado en `src/models/train_challengers.py`.

Modelo evaluado:

- `random_forest_challenger`: Random Forest con el mismo contrato de features que el baseline.
- Preprocessing: One-Hot Encoding para categoricas, binarias en passthrough y numericas sin escalado porque el modelo es de arboles.
- Artefacto guardado: `models/challengers/random_forest_challenger.pkl`.

Resultados de validacion frente al baseline:

- Logistic Regression: F1-score clase `Canceled` = 0,6870; ROC-AUC = 0,8604.
- Random Forest optimizado: F1-score clase `Canceled` = 0,8042; ROC-AUC = 0,9347.
- Gap train-validacion en F1 de Random Forest optimizado: 0,0242.
- Resultado de overfitting: cumple la regla de diferencia inferior a 0,05.

Validacion cruzada:

- Estrategia: Stratified K-Fold de 3 folds.
- F1 medio clase `Canceled`: 0,8160.
- Desviacion F1: 0,0071.
- ROC-AUC medio: 0,9426.
- Desviacion ROC-AUC: 0,0017.

Decision actual:

- Random Forest queda seleccionado como Champion Model.
- El artefacto versionado se encuentra en `models/champion/random_forest_champion.pkl`.
- La metadata del Champion se encuentra en `models/champion/champion_metadata.json`.
- FastAPI carga el Champion desde la metadata y expone su version en `GET /model/info` y `POST /predict`.
- El frontend principal consume reservas candidatas desde `GET /reservations/demo`, calcula predicciones reales con `POST /predict` y registra feedback real con `POST /feedback`.
- El holdout final se evaluo una unica vez: F1 `Canceled` 0,8258, ROC-AUC 0,9499 y gap F1 validacion-test 0,0153.
- La evidencia queda registrada en `reports/champion_test_metrics.json`; el test queda cerrado para nuevos ajustes.

## Estado del tuning inicial

Busqueda controlada ejecutada para `RandomForestClassifier`.

Configuracion ganadora aplicada:

- `n_estimators=200`.
- `max_depth=18`.
- `min_samples_leaf=6`.
- `min_samples_split=12`.
- `class_weight="balanced_subsample"`.

Comparacion de validacion:

- Random Forest inicial (`max_depth=14`, `min_samples_leaf=12`): F1 = 0,7952; gap = 0,0186; ROC-AUC = 0,9287.
- Random Forest intermedio (`max_depth=16`, `min_samples_leaf=8`): F1 = 0,8042; gap = 0,0242; ROC-AUC = 0,9347.
- Random Forest final (`max_depth=18`, `min_samples_leaf=6`): F1 = 0,8105; gap = 0,0345; ROC-AUC = 0,9391.

Decision actual:

- La configuracion final mejora el F1 de validacion y mantiene overfitting inferior a 0,05.
- La configuracion esta aplicada en `src/models/train_challengers.py`, el artefacto esta regenerado en `models/challengers/random_forest_challenger.pkl` y la verificacion queda cubierta por `tests/unit/test_challenger_training.py`.

## Metricas obligatorias

El informe tecnico debe incluir:

- Accuracy.
- Precision.
- Recall.
- F1-score.
- ROC-AUC cuando aplique.
- Matriz de confusion.
- Curva ROC cuando aplique.
- Feature importance o alternativa equivalente.
- Analisis de errores.

Si el problema es multiclase, se deben reportar promedios macro y weighted cuando sea relevante.

### Metrica principal

La metrica principal del proyecto es:

```text
F1-score de la clase Canceled
```

Justificacion:

- El objetivo de negocio es anticipar reservas con riesgo de cancelacion.
- El target tiene desbalance moderado: `Not_Canceled` es la clase mayoritaria.
- `Accuracy` puede resultar enganosa si el modelo predice bien la clase mayoritaria pero falla cancelaciones.
- F1-score equilibra `precision` y `recall`, por lo que evita priorizar solo volumen de alertas o solo cobertura de cancelaciones.

Metricas secundarias:

- `recall` de la clase `Canceled`, para medir cuantas cancelaciones reales detecta el modelo.
- `precision` de la clase `Canceled`, para medir cuantas alertas son realmente utiles.
- `ROC-AUC`, para evaluar separacion general entre clases.
- Matriz de confusion, para explicar errores a negocio.
- `accuracy`, solo como referencia complementaria.

## Regla de overfitting

El overfitting debe ser inferior al 5%.

Regla operativa:

- Usar como metrica principal el F1-score de la clase `Canceled`.
- Calcular F1-score de `Canceled` en train.
- Calcular F1-score de `Canceled` en validacion o cross-validation.
- La diferencia absoluta entre train y validacion debe ser menor a 0.05.

Ejemplo:

- F1 train = 0.86.
- F1 validacion = 0.83.
- Diferencia = 0.03.
- Resultado: aceptado.

Si la diferencia es igual o superior a 0.05, el modelo no puede ser Champion hasta aplicar regularizacion, simplificacion, mejores splits, tuning o seleccion de features.

## Modelos

### Baseline simple

Objetivo: tener una primera referencia rapida y reproducible.

Opciones validas:

- Logistic Regression.
- Decision Tree limitado.
- K-Nearest Neighbors.
- DummyClassifier como referencia minima adicional.

Debe incluir:

- Pipeline de preprocesamiento.
- Split reproducible.
- Metricas de train y validacion.
- Matriz de confusion.
- Registro en tabla de experimentos.

### Modelo ensemble

Objetivo: alcanzar Nivel Medio con un modelo mas robusto.

Opciones validas:

- Random Forest.
- Gradient Boosting.
- XGBoost, LightGBM o CatBoost si se instalan y justifican.

Debe incluir:

- Validacion cruzada.
- Tuning de hiperparametros.
- Evaluacion de overfitting.
- Feature importance.

### Modelo Champion

Modelo seleccionado para productivizar.

Estado actual:

- Champion productivizado: `random_forest_champion_v0.1.0`.
- Artefacto cargado por FastAPI: `models/champion/random_forest_champion.pkl`.
- Metadata del Champion: `models/champion/champion_metadata.json`.
- Endpoint de inferencia: `POST /predict`.
- Endpoint de metadata: `GET /model/info`.
- La API usa el Champion Random Forest y mantiene el contrato de entrada/salida definido para la app.

Debe cumplir:

- Mejor equilibrio entre metrica principal, overfitting, interpretabilidad y estabilidad.
- Overfitting inferior al 5%.
- Preprocesamiento reproducible en pipeline.
- Artefacto guardado con version.
- Compatible con la app.
- Documentado en informe tecnico.

### Modelo Challenger

Modelo alternativo que compite contra el Champion.

Debe cumplir:

- Usar el mismo contrato de inputs que el Champion.
- Tener metricas calculadas con el mismo split o validacion.
- No reemplazar automaticamente al Champion sin pasar reglas de aceptacion.

### Red neuronal experimental

Objetivo: cubrir Nivel Experto como experimento comparativo.

Debe cumplir:

- Usar train, validacion y test comparables.
- Reportar las mismas metricas que los modelos clasicos.
- Documentar si mejora o no mejora al Champion.
- No bloquear la entrega esencial.

## Reglas de seleccion del Champion

Un modelo puede ser Champion si:

- Supera al baseline en la metrica principal.
- Cumple overfitting inferior al 5%.
- No empeora de forma grave metricas secundarias.
- Tiene pipeline de inferencia reproducible.
- Puede cargarse desde la app.
- Tiene matriz de confusion y analisis de errores.
- Tiene version registrada en tabla de experimentos.

Si dos modelos tienen rendimiento similar, se prefiere:

1. Menor overfitting.
2. Mayor simplicidad operativa.
3. Mayor interpretabilidad.
4. Menor coste de inferencia.

## Reglas de A/B Testing

Objetivo: comparar Champion contra Challenger en entorno controlado o simulado.

Contrato minimo:

- Champion recibe el trafico principal.
- Challenger recibe una porcion menor o un conjunto simulado equivalente.
- Cada prediccion registra un `prediction_id` unico y `model_version`.
- Toda respuesta correcta de `POST /predict` guarda input validado, prediccion, etiqueta, probabilidad, riesgo, timestamp, fuente y version de modelo en `prediction_logs`.
- El feedback se mantiene en `prediction_feedback` y puede existir solo para una parte de las predicciones.
- La comparacion usa la misma metrica principal definida en la spec.

Regla inicial sugerida:

- 80% Champion.
- 20% Challenger.

Estado actual: pendiente de evaluacion en la proxima sesion. El equipo debe decidir si el A/B sera real en app, simulado con un conjunto de evaluacion o documentado como experimento offline. Ninguna alternativa queda descartada todavia.

## Reglas de Data Drift

Objetivo: detectar si los datos nuevos se alejan de los datos de entrenamiento.

Contrato implementado:

- El perfil de referencia se genera exclusivamente con el split de entrenamiento estratificado y queda versionado en `models/monitoring/training_reference_profile.json`.
- Los datos actuales proceden de las inferencias persistidas en `prediction_logs`; no requieren que el resultado real este etiquetado.
- Cada llamada registra origen mediante `X-Prediction-Source`: `api`, `frontend_manual` o `frontend_demo_queue`.
- El calculo usa las 1.000 predicciones operativas mas recientes y excluye `frontend_demo_queue` y el origen heredado sin clasificar `prediction_api`.
- Se calcula PSI para todas las variables del contrato de entrada.
- El calculo requiere al menos 100 registros actuales validos; con menos datos devuelve `insufficient_data`.
- `GET /monitoring/drift` publica estado global, PSI maximo, variables alertadas y detalle por variable.

Metodo implementado:

- Variables numericas: PSI sobre intervalos definidos por deciles del entrenamiento.
- Variables categoricas y binarias: PSI sobre frecuencias de entrenamiento, incluyendo una categoria controlada para valores nuevos.

Umbrales operativos de PSI:

- PSI < 0.10: sin drift relevante.
- 0.10 <= PSI < 0.25: drift moderado, revisar.
- PSI >= 0.25: drift alto, considerar reentrenamiento.

Estados globales:

- `insufficient_data`: menos de 100 registros actuales validos.
- `stable`: todas las variables tienen PSI inferior a 0.10.
- `warning`: existe drift moderado y no existe drift alto.
- `drift_detected`: al menos una variable tiene PSI igual o superior a 0.25.

El drift por si solo no autoriza auto-reemplazo; solo indica que se debe evaluar un nuevo modelo. Todas las inferencias siguen auditadas aunque una fuente quede excluida de la muestra PSI.

## Reglas de auto-reemplazo

Un modelo nuevo solo puede reemplazar al Champion si:

- Usa el mismo contrato de datos o una migracion documentada.
- Pasa tests de preprocesamiento e inferencia.
- Mejora la metrica principal por un margen definido.
- Mantiene overfitting inferior al 5%.
- No empeora metricas criticas por encima de un umbral aceptado.
- Tiene evaluacion en validacion o test comparable.
- Tiene version, fecha y artefacto guardado.
- Queda documentado en la tabla de experimentos.

Estado actual: pendiente de evaluacion en la proxima sesion. Si se aprueba su implementacion, debe fijarse el margen minimo de mejora; la sugerencia inicial es +0.02 absoluto en la metrica principal.

Para entrega academica, el auto-reemplazo puede implementarse como script controlado y documentado, no necesariamente como servicio autonomo permanente.

## Estructura de carpetas recomendada

No crear todas las carpetas hasta que sean necesarias. Esta es la estructura objetivo:

```text
.
|-- .specify/
|   |-- 1_intent.md
|   |-- 2_spec.md
|   |-- 3_plan.md
|   `-- 4_tasks.md
|-- alembic/
|   |-- versions/
|   `-- env.py
|-- app/
|   |-- frontend/
|   |   |-- Dockerfile
|   |   |-- nginx.conf
|   |   |-- src/
|   |   |-- package.json
|   |   `-- vite.config.js
|   `-- backend/
|       |-- Dockerfile
|       |-- __init__.py
|       |-- main.py
|       `-- schemas.py
|-- data/
|   |-- raw/
|   |-- interim/
|   |-- processed/
|   `-- feedback/
|-- docs/
|   |-- business_presentation/
|   |-- project_management/
|   `-- technical_presentation/
|-- models/
|   |-- champion/
|   `-- challengers/
|-- notebooks/
|-- reports/
|   |-- figures/
|   `-- model_report.md
|-- src/
|   |-- data/
|   |-- features/
|   |-- models/
|   |-- evaluation/
|   `-- mlops/
|-- tests/
|-- .github/
|   `-- pull_request_template.md
|-- .dockerignore
|-- alembic.ini
|-- CHANGELOG.md
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

## Contrato de app

La app debe:

- Mostrar un formulario con inputs equivalentes a las features del modelo.
- Mostrar reservas candidatas obtenidas desde el backend, no desde fixtures locales.
- Validar tipos y rangos basicos.
- Ejecutar el mismo preprocesamiento usado en entrenamiento.
- Devolver la clase predicha.
- Devolver probabilidad o confianza si aplica.
- Mostrar version del modelo usada.
- Permitir recoger feedback del usuario si se implementa Nivel Medio.

### Inputs del usuario

Inputs definitivos: definidos por `PredictionRequest` en `app/backend/schemas.py` y documentados en `docs/api_contract.md`.

Cada input debe documentarse con:

- Nombre visible.
- Nombre tecnico de feature.
- Tipo de dato.
- Rango o valores permitidos.
- Valor por defecto.
- Si es obligatorio u opcional.

### Salida de prediccion

La salida minima debe incluir:

- Clase predicha.
- Probabilidad o confianza si el modelo la expone.
- Mensaje corto interpretable para negocio.
- Identificador unico y version del modelo.
- Nivel de riesgo y recomendacion operativa.
- Hasta tres factores locales ordenados por impacto estimado, sin presentarlos como relaciones causales.

### Guardado de feedback

Feedback implementado:

- Timestamp.
- Model version.
- Inputs validados.
- Prediccion.
- Probabilidad si aplica.
- Feedback del usuario.
- Target real si se conoce posteriormente.
- Fuente del registro.
- Comentarios opcionales.

Estado actual:

- Endpoint de escritura: `POST /feedback`.
- Endpoint de resumen: `GET /feedback/summary`.
- Endpoint de historico: `GET /feedback`.
- Endpoint de correccion: `PATCH /feedback/{record_id}`.
- Almacenamiento local por defecto: SQLite en `data/app/hotel_insights.db`.
- Almacenamiento desplegado: PostgreSQL administrado en Amazon RDS mediante `DATABASE_URL`.
- La base local y los archivos de entorno operativos se ignoran en Git.
- Utilidad de ingesta para reentrenamiento: `src/data/feedback_ingestion.py`.
- El dataset de reentrenamiento se construye solo con registros que tienen `actual_status` conocido.

## Base de datos o almacenamiento

Nivel Medio minimo:

- Guardar feedback y datos nuevos en CSV o SQLite.
- Estado actual: cubierto con SQLite local mediante SQLAlchemy.

Nivel Avanzado recomendado:

- SQLite o PostgreSQL para predicciones y feedback.
- Estado actual: cubierto con PostgreSQL en Amazon RDS para el despliegue AWS.
- La misma capa SQLAlchemy usa SQLite como alternativa local y PostgreSQL en producción.
- Alembic `1.18.5` versiona el esquema mediante revisiones auditables.
- Revision actual: `0002_prediction_logs`.
- El backend ejecuta `alembic upgrade head` antes de iniciar FastAPI en local, Docker y AWS.
- La migracion inicial adopta la tabla historica solo si su contrato de columnas coincide; cualquier incompatibilidad detiene el arranque sin modificar datos.
- La segunda migracion crea `prediction_logs` para auditar todas las respuestas correctas de inferencia.

No guardar datos personales sensibles salvo que sean estrictamente necesarios y esten justificados.

## Tests minimos

Tests requeridos para Nivel Avanzado:

- Validacion de schema de datos.
- Preprocesamiento sin errores con datos validos.
- Prediccion devuelve clase esperada de tipo correcto.
- Modelo cargado tiene version.
- Metricas minimas aceptables.
- Overfitting inferior al 5%.
- App smoke test o test de funcion de prediccion.
- Drift calcula resultado sin romper con datos de ejemplo.

## Docker

Docker debe permitir:

- Instalar dependencias.
- Aplicar migraciones pendientes antes de arrancar la API.
- Levantar la app.
- Cargar el modelo Champion.
- Exponer el puerto de la app.
- Documentar el comando de ejecucion.

Tecnologia de app definida: frontend React + Vite y backend de inferencia con FastAPI.

Backend operativo disponible:

- `GET /health`.
- `GET /health/ready` comprueba que el Champion esta disponible y que la base de datos contiene las tablas operativas migradas.
- `GET /model/info`.
- `GET /reservations/demo` con reservas reales derivadas del CSV de `data/raw/`.
- `POST /predict` con inferencia del Champion Random Forest.
- `POST /feedback`.
- `GET /feedback/summary`.
- `GET /feedback`.
- `PATCH /feedback/{record_id}`.
- `GET /monitoring/drift`.
- Contrato documentado en `docs/api_contract.md`.

Docker validado disponible:

- `app/backend/Dockerfile`.
- `app/frontend/Dockerfile`.
- `docker-compose.yml`.
- Backend expuesto en `http://localhost:8000`.
- Frontend expuesto en `http://localhost:8080`.
- Validado con Champion Random Forest `random_forest_champion_v0.1.0`.
- Validado con endpoints `GET /health`, `GET /health/ready`, `GET /model/info`, `GET /reservations/demo`, `POST /predict`, `POST /feedback`, `GET /feedback/summary`, `GET /feedback`, `PATCH /feedback/{record_id}` y `GET /monitoring/drift`.
- Frontend validado con `curl.exe -I http://localhost:8080/` y respuesta `HTTP/1.1 200 OK`.
- `docker-compose.ec2.yml` disponible para la ejecución en AWS con PostgreSQL externo.
- `scripts/deploy_ec2.sh` valida configuracion, reconstruye servicios y espera el readiness check antes de completar el despliegue.
- `scripts/start_backend.sh` ejecuta las migraciones Alembic antes de iniciar Uvicorn.

Observabilidad operativa:

- Cada respuesta incluye `X-Request-ID`; se conserva un identificador seguro del cliente o se genera un UUID.
- FastAPI emite logs JSON de solicitud con metodo, ruta, estado y duracion, sin payloads ni credenciales.
- Cada inferencia correcta emite un evento correlacionado por `request_id` y `prediction_id`.
- `GET /health` se usa como liveness y `GET /health/ready` como readiness para Docker y AWS.

## Despliegue web y CI/CD

Despliegue operativo disponible en AWS:

- URL pública HTTPS: `https://d3lxpalnzir74p.cloudfront.net`.
- CloudFront como punto de entrada público y terminación HTTPS.
- EC2 con Docker Compose para nginx, frontend React y backend FastAPI.
- RDS PostgreSQL privado para feedback y datos operativos.
- GitHub Actions despliega automáticamente cada merge en `develop`.
- Autenticación GitHub-AWS mediante OIDC, sin claves AWS permanentes en GitHub.
- AWS Systems Manager ejecuta el despliegue sin depender de SSH desde CI.
- El puerto HTTP de EC2 solo admite orígenes de la lista administrada de CloudFront.

Guía operativa: `docs/aws_deployment.md`.

## Documentacion e informes

El proyecto debe incluir:

- README actualizado.
- Informe tecnico de rendimiento.
- Tabla de experimentos.
- Capturas de app.
- Presentacion de negocio.
- Presentacion tecnica del codigo.
- Enlace al tablero Jira oficial.

## Criterios de cierre por nivel

### Nivel Esencial

El nivel esta cerrado si:

- Dataset cargado.
- Target definido.
- EDA documentado con visualizaciones.
- Baseline entrenado.
- Metricas obligatorias calculadas.
- Overfitting inferior al 5%.
- App funcional con prediccion usando el Champion.
- Informe tecnico inicial.
- README con instalacion y ejecucion.

Estado actual: cubierto. La validacion manual de demo esta documentada en `reports/manual_app_validation.md`. Queda revision final de redaccion antes de entrega.

### Nivel Medio

El nivel esta cerrado si:

- Modelo ensemble entrenado.
- Validacion cruzada aplicada.
- Hiperparametros optimizados.
- Champion seleccionado.
- Feedback guardado.
- Datos nuevos disponibles para futuro reentrenamiento.

Estado actual: cubierto salvo posibles mejoras de producto sobre la interfaz visual de feedback.
El frontend principal ya no depende de datos mock para tabla, alertas ni feedback del modal.

### Nivel Avanzado

El nivel esta cerrado si:

- Docker funcional.
- Base de datos o almacenamiento persistente conectado.
- Tests unitarios minimos.
- App desplegada o preparada para despliegue.
- Smoke test documentado.

Estado actual: cubierto. Docker, PostgreSQL en RDS, tests, smoke test, despliegue HTTPS en AWS y entrega automática desde `develop` están verificados.

### Nivel Experto

El nivel esta cerrado si:

- Red neuronal entrenada y comparada.
- A/B Testing implementado o simulado con evidencia.
- Data Drift calculado.
- Auto-reemplazo condicionado por metricas.
- Dashboard o reporte de monitoreo.
- Ciclo MLOps explicado en documentacion.

Estado actual:

- Data Drift esta implementado, probado y documentado mediante perfil versionado, PSI, auditoria de predicciones y `GET /monitoring/drift`.
- Red neuronal experimental, A/B Testing y auto-reemplazo condicionado siguen pendientes y se evaluaran en la proxima sesion; no se descarta ninguno de los tres requisitos.
- La documentacion final del ciclo MLOps se cerrara cuando el equipo decida el alcance de esos tres experimentos.
