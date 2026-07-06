# SPEC 2 - Technical Specification

Este archivo es la Single Source of Truth del proyecto. Toda implementacion debe respetar este contrato o actualizarlo de forma explicita antes de cambiar el alcance.

## Estado actual

- Repositorio: `proyecto5-grupo2`.
- README inicial: existe, pero aun no documenta instalacion ni decisiones tecnicas.
- Dataset: Hotel Reservations Classification Dataset.
- Archivo esperado: `Hotel Reservations.csv`.
- Fuente de referencia: Kaggle, kernel `marawaneslam/hotel-reservations-classification`.
- Ruta original en Kaggle: `/kaggle/input/hotel-reservations-classification-dataset/Hotel Reservations.csv`.
- Cliente del proyecto: plataforma de reservas hoteleras tipo Booking, Trivago o Agoda.
- Problema de negocio: predecir si una reserva sera cancelada.
- Target: `booking_status`.
- Metrica principal inicial: F1-score de la clase `Canceled`, complementada con precision, recall, ROC-AUC y matriz de confusion.
- Tecnologia de app: TODO: elegir entre Streamlit, Gradio, Dash o API + frontend simple.
- Sistema de gestion: TODO: agregar enlace a Trello u otra herramienta.

## Tipo de problema

- Tipo: clasificacion supervisada binaria.
- Entrada: variables tabulares del dataset elegido.
- Salida: estado de la reserva predicho.
- Salida opcional: probabilidad o confianza de la prediccion si el modelo lo permite.

## Dataset

Dataset definitivo: Hotel Reservations Classification Dataset.

Archivo de trabajo esperado: `Hotel Reservations.csv`.

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
- Distribucion de clases: `Not_Canceled` 24.390 registros (67,24%) y `Canceled` 11.885 registros (32,76%).
- Si hay desbalance: hay desbalance moderado, por lo que `accuracy` no debe usarse como unica metrica.
- Si se requiere binarizacion o agrupacion: no requiere agrupacion; para modelos se codificara como variable binaria.
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

## Regla de overfitting

El overfitting debe ser inferior al 5%.

Regla operativa:

- Metrica principal operativa: F1-score de la clase `Canceled`.
- Calcular la metrica en train.
- Calcular la misma metrica en validacion o cross-validation.
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
- Cada prediccion registra `model_version`.
- Se guarda input validado, prediccion, probabilidad si aplica, timestamp y feedback si existe.
- La comparacion usa la misma metrica principal definida en la spec.

Regla inicial sugerida:

- 80% Champion.
- 20% Challenger.

TODO: confirmar si el A/B sera real en app, simulado con dataset holdout o documentado como experimento offline.

## Reglas de Data Drift

Objetivo: detectar si los datos nuevos se alejan de los datos de entrenamiento.

Contrato minimo:

- Comparar distribucion de datos de entrenamiento contra datos nuevos o feedback acumulado.
- Medir drift por feature relevante.
- Generar alerta si el drift supera umbral.

Metodos sugeridos:

- PSI para variables numericas o discretizadas.
- KS Test para variables numericas.
- Chi-square o distribucion de frecuencias para categoricas.

Umbrales sugeridos para PSI:

- PSI < 0.10: sin drift relevante.
- 0.10 <= PSI < 0.25: drift moderado, revisar.
- PSI >= 0.25: drift alto, considerar reentrenamiento.

El drift por si solo no autoriza auto-reemplazo. Solo indica que se debe evaluar un nuevo modelo.

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

TODO: definir margen minimo de mejora para reemplazo. Sugerencia inicial: +0.02 absoluto en la metrica principal.

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
|-- app/
|   |-- main.py
|   `-- components/
|-- data/
|   |-- raw/
|   |-- interim/
|   |-- processed/
|   `-- feedback/
|-- docs/
|   |-- business_presentation/
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
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

## Contrato de app

La app debe:

- Mostrar un formulario con inputs equivalentes a las features del modelo.
- Validar tipos y rangos basicos.
- Ejecutar el mismo preprocesamiento usado en entrenamiento.
- Devolver la clase predicha.
- Devolver probabilidad o confianza si aplica.
- Mostrar version del modelo usada.
- Permitir recoger feedback del usuario si se implementa Nivel Medio.

### Inputs del usuario

Inputs definitivos: TODO.

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

### Guardado de feedback

Feedback minimo recomendado:

- Timestamp.
- Model version.
- Inputs validados.
- Prediccion.
- Probabilidad si aplica.
- Feedback del usuario.
- Target real si se conoce posteriormente.

## Base de datos o almacenamiento

Nivel Medio minimo:

- Guardar feedback y datos nuevos en CSV o SQLite.

Nivel Avanzado recomendado:

- SQLite o PostgreSQL para predicciones y feedback.

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
- Levantar la app.
- Cargar el modelo Champion.
- Exponer el puerto de la app.
- Documentar el comando de ejecucion.

TODO: definir puerto y tecnologia de app.

## Documentacion e informes

El proyecto debe incluir:

- README actualizado.
- Informe tecnico de rendimiento.
- Tabla de experimentos.
- Capturas de app.
- Presentacion de negocio.
- Presentacion tecnica del codigo.
- Enlace a Trello o herramienta equivalente.

## Criterios de cierre por nivel

### Nivel Esencial

El nivel esta cerrado si:

- Dataset cargado.
- Target definido.
- EDA documentado con visualizaciones.
- Baseline entrenado.
- Metricas obligatorias calculadas.
- Overfitting inferior al 5%.
- App funcional con prediccion.
- Informe tecnico inicial.
- README con instalacion y ejecucion.

### Nivel Medio

El nivel esta cerrado si:

- Modelo ensemble entrenado.
- Validacion cruzada aplicada.
- Hiperparametros optimizados.
- Champion seleccionado.
- Feedback guardado.
- Datos nuevos disponibles para futuro reentrenamiento.

### Nivel Avanzado

El nivel esta cerrado si:

- Docker funcional.
- Base de datos o almacenamiento persistente conectado.
- Tests unitarios minimos.
- App desplegada o preparada para despliegue.
- Smoke test documentado.

### Nivel Experto

El nivel esta cerrado si:

- Red neuronal entrenada y comparada.
- A/B Testing implementado o simulado con evidencia.
- Data Drift calculado.
- Auto-reemplazo condicionado por metricas.
- Dashboard o reporte de monitoreo.
- Ciclo MLOps explicado en documentacion.
