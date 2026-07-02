# SPEC 2 - Technical Specification

Este archivo es la Single Source of Truth del proyecto. Toda implementacion debe respetar este contrato o actualizarlo de forma explicita antes de cambiar el alcance.

## Estado actual

- Repositorio: `proyecto5-grupo2`.
- README inicial: existe, pero aun no documenta instalacion ni decisiones tecnicas.
- Dataset: TODO.
- Target: TODO.
- Metrica principal: TODO.
- Tecnologia de app: TODO: elegir entre Streamlit, Gradio, Dash o API + frontend simple.
- Sistema de gestion: TODO: agregar enlace a Trello u otra herramienta.

## Tipo de problema

- Tipo: clasificacion supervisada.
- Entrada: variables tabulares del dataset elegido.
- Salida: clase predicha.
- Salida opcional: probabilidad o confianza de la prediccion si el modelo lo permite.

## Dataset

Dataset definitivo: TODO.

Si el equipo no elige otro dataset, puede evaluar el dataset sugerido en la consigna: Airlines Dataset.

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

Target definitivo: TODO.

Debe documentarse:

- Nombre de columna.
- Clases posibles.
- Distribucion de clases.
- Si hay desbalance.
- Si se requiere binarizacion o agrupacion.
- Justificacion de por que es una variable de clasificacion valida.

### Features esperadas

Features definitivas: TODO.

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

- Elegir una metrica principal: TODO.
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
