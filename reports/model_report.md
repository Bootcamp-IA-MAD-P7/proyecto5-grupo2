# Model Report

## Baseline inicial

Este reporte registra el primer baseline reproducible del proyecto. El objetivo no es elegir todavia el modelo final, sino crear una primera comparacion honesta entre una regla minima y un modelo real simple.

### Modelos evaluados

- `dummy_most_frequent`: modelo de referencia que siempre predice la clase mayoritaria.
- `logistic_regression_balanced`: primer modelo real, usando el pipeline de preprocesamiento y ajuste de pesos para compensar el desbalance moderado del target.

### Datos y target

- Dataset: Hotel Reservations Classification Dataset.
- Target: `booking_status`.
- Clase positiva para metricas principales: `Canceled`.
- Split usado: train 70%, validacion 15%, test 15%.
- Durante entrenamiento, tuning y seleccion, el test permanecio reservado; su evaluacion final se documenta en la seccion del Champion.

### Metricas train/validacion

| model_name | split | accuracy | precision_canceled | recall_canceled | f1_canceled | roc_auc | true_negative | false_positive | false_negative | true_positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dummy_most_frequent | train | 0.6724 | 0.0 | 0.0 | 0.0 | 0.5 | 17072 | 0 | 8319 | 0 |
| dummy_most_frequent | validation | 0.6724 | 0.0 | 0.0 | 0.0 | 0.5 | 3659 | 0 | 1783 | 0 |
| logistic_regression_balanced | train | 0.7793 | 0.635 | 0.7673 | 0.6949 | 0.8624 | 13403 | 3669 | 1936 | 6383 |
| logistic_regression_balanced | validation | 0.7732 | 0.6271 | 0.7594 | 0.687 | 0.8604 | 2854 | 805 | 429 | 1354 |

### Figuras de validacion

- Matriz de confusion: `reports/figures/baseline_logistic_confusion_matrix.png`.
- Curva ROC: `reports/figures/baseline_logistic_roc_curve.png`.

### Revision inicial de overfitting

La regla del proyecto pide que la diferencia absoluta entre train y validacion sea menor a 0.05 en la metrica principal. Para este baseline usamos F1-score de la clase `Canceled`.

| model_name | train | validation | absolute_gap | passes_under_5_percent_rule |
| --- | --- | --- | --- | --- |
| dummy_most_frequent | 0.0 | 0.0 | 0.0 | True |
| logistic_regression_balanced | 0.6949 | 0.687 | 0.0079 | True |

### Lectura de resultados

- El `DummyClassifier` sirve como piso minimo: si un modelo real no lo supera, no aporta valor.
- La Logistic Regression mejora el F1-score de validacion de la clase `Canceled` hasta 0.6870.
- La diferencia train-validacion queda dentro de la regla de overfitting inferior al 5%.
- El siguiente paso sera revisar si un modelo ensemble mejora este baseline sin aumentar demasiado el overfitting.

## Ensemble challenger - Random Forest

### Ticket relacionado

- `T-3.1 Entrenar modelo ensemble`.
- `T-3.2 Aplicar validacion cruzada`.
- `T-3.3 Optimizar hiperparametros`.

### Busqueda de hiperparametros

Se evaluaron 12 configuraciones controladas de `RandomForestClassifier` usando el mismo split train/validacion. El criterio de seleccion fue maximizar el F1-score de la clase `Canceled` en validacion, manteniendo la regla de overfitting inferior a 0.05.

Tabla completa exportada en `reports/random_forest_tuning_results.csv`.

Top 5 de configuraciones:

| candidate | n_estimators | max_depth | min_samples_leaf | min_samples_split | class_weight | validation_f1_canceled | absolute_gap | validation_roc_auc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rf_depth18_leaf6_split12 | 200 | 18 | 6 | 12 | balanced_subsample | 0.8105 | 0.0345 | 0.9391 |
| rf_depth20_leaf8_split16 | 200 | 20 | 8 | 16 | balanced_subsample | 0.8092 | 0.0301 | 0.937 |
| rf_depth16_leaf6_split12 | 200 | 16 | 6 | 12 | balanced_subsample | 0.8077 | 0.0287 | 0.9373 |
| rf_depth16_leaf8_split24 | 200 | 16 | 8 | 24 | balanced_subsample | 0.8066 | 0.0204 | 0.9339 |
| rf_depth16_leaf8_split16_300 | 300 | 16 | 8 | 16 | balanced_subsample | 0.8051 | 0.0229 | 0.9352 |

### Configuracion del challenger

- Modelo: `RandomForestClassifier`.
- Preprocessing: mismo contrato de features que el baseline, con One-Hot Encoding para categoricas y sin escalado numerico porque el modelo es de arboles.
- Hiperparametros optimizados: `n_estimators=200`, `max_depth=18`, `min_samples_leaf=6`, `min_samples_split=12`, `class_weight='balanced_subsample'`.
- Clase positiva: `Canceled`.
- El test sigue reservado para evaluacion final.

### Comparacion train/validacion

| model_name | split | accuracy | precision_canceled | recall_canceled | f1_canceled | roc_auc | true_negative | false_positive | false_negative | true_positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dummy_most_frequent | train | 0.6724 | 0.0 | 0.0 | 0.0 | 0.5 | 17072 | 0 | 8319 | 0 |
| dummy_most_frequent | validation | 0.6724 | 0.0 | 0.0 | 0.0 | 0.5 | 3659 | 0 | 1783 | 0 |
| logistic_regression_balanced | train | 0.7793 | 0.635 | 0.7673 | 0.6949 | 0.8624 | 13403 | 3669 | 1936 | 6383 |
| logistic_regression_balanced | validation | 0.7732 | 0.6271 | 0.7594 | 0.687 | 0.8604 | 2854 | 805 | 429 | 1354 |
| random_forest_challenger | train | 0.8974 | 0.8369 | 0.8532 | 0.845 | 0.9665 | 15689 | 1383 | 1221 | 7098 |
| random_forest_challenger | validation | 0.8752 | 0.8067 | 0.8144 | 0.8105 | 0.9391 | 3311 | 348 | 331 | 1452 |

### Revision de overfitting

| model_name | train | validation | absolute_gap | passes_under_5_percent_rule |
| --- | --- | --- | --- | --- |
| dummy_most_frequent | 0.0 | 0.0 | 0.0 | True |
| logistic_regression_balanced | 0.6949 | 0.687 | 0.0079 | True |
| random_forest_challenger | 0.845 | 0.8105 | 0.0345 | True |

### Validacion cruzada del challenger

| model_name | metric | cv_mean | cv_std | cv_splits |
| --- | --- | --- | --- | --- |
| random_forest_challenger | f1_canceled | 0.816 | 0.0071 | 3 |
| random_forest_challenger | precision_canceled | 0.8101 | 0.0083 | 3 |
| random_forest_challenger | recall_canceled | 0.822 | 0.0079 | 3 |
| random_forest_challenger | roc_auc | 0.9426 | 0.0017 | 3 |

### Lectura tecnica

- El Random Forest mejora el F1-score de validacion de `Canceled` de 0.6870 a 0.8105.
- El gap train-validacion del challenger es 0.0345, por debajo del limite operativo de 0.05.
- La validacion cruzada de 3 folds muestra F1 medio de 0.8160.
- Este modelo queda como challenger optimizado y base del Champion promocionado en `T-3.4`.

## Champion Model Selection

### Decision

Se selecciona `random_forest_champion_v0.1.0` como Champion Model del proyecto.

### Evidencia de seleccion

| criterio | baseline Logistic Regression | Champion Random Forest |
| --- | --- | --- |
| F1 validacion clase `Canceled` | 0.6870 | 0.8105 |
| Precision validacion clase `Canceled` | 0.6271 | 0.8067 |
| Recall validacion clase `Canceled` | 0.7594 | 0.8144 |
| ROC-AUC validacion | 0.8604 | 0.9391 |
| Gap F1 train-validacion | 0.0079 | 0.0345 |
| Regla overfitting < 0.05 | cumple baseline | True |

### Validacion cruzada del Champion

| metrica | media | desviacion | folds |
| --- | --- | --- | --- |
| F1 `Canceled` | 0.8160 | 0.0071 | 3 |
| Precision `Canceled` | 0.8101 | 0.0083 | 3 |
| Recall `Canceled` | 0.8220 | 0.0079 | 3 |
| ROC-AUC | 0.9426 | 0.0017 | 3 |

### Artefactos versionados

- Modelo Champion: `models/champion/random_forest_champion.pkl`.
- Metadata Champion: `models/champion/champion_metadata.json`.
- Version: `random_forest_champion_v0.1.0`.
- Hiperparametros: `n_estimators=200`, `max_depth=18`, `min_samples_leaf=6`, `min_samples_split=12`, `class_weight='balanced_subsample'`.

### Lectura tecnica

- El Champion mejora el F1-score de validacion de `Canceled` de 0.6870 a 0.8105.
- El gap train-validacion del Champion es 0.0345, por debajo del limite operativo de 0.05.
- La validacion cruzada confirma estabilidad razonable: F1 medio 0.8160 con desviacion 0.0071.
- La API ya carga este Champion desde `models/champion/random_forest_champion.pkl` usando la metadata versionada.

### Evaluacion final sobre test reservado

El holdout final se abrio una unica vez el 15 de julio de 2026, despues de congelar el Champion y declarar previamente los criterios de aceptacion en `docs/champion_holdout_protocol.md`.

| metrica test | resultado |
| --- | ---: |
| Accuracy | 0.8855 |
| Precision `Canceled` | 0.8233 |
| Recall `Canceled` | 0.8284 |
| F1 `Canceled` | 0.8258 |
| ROC-AUC | 0.9499 |
| True negative | 3342 |
| False positive | 317 |
| False negative | 306 |
| True positive | 1477 |

- Filas de test: 5442, equivalentes al 15 % del dataset.
- Gap absoluto F1 validacion-test: 0.0153.
- Criterio F1 test >= 0.80: cumple.
- Criterio gap validacion-test <= 0.05: cumple.
- Evidencia reproducible: `reports/champion_test_metrics.json` y `models/champion/champion_metadata.json`.
- El test queda cerrado y no se utilizara para tuning o seleccion posterior.

### Tabla de experimentos y decision

Esta tabla resume los modelos evaluados durante el proyecto y la decision tomada sobre cada uno. La metrica principal es el F1-score de la clase `Canceled`, porque el objetivo de negocio es anticipar cancelaciones sin depender solo de la clase mayoritaria.

| experimento | familia | configuracion principal | f1_train_canceled | f1_validation_canceled | gap_f1 | validation_roc_auc | decision |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `dummy_most_frequent` | Regla base | Predice siempre `Not_Canceled` | 0.0000 | 0.0000 | 0.0000 | 0.5000 | Descartado: solo sirve como piso minimo, no detecta cancelaciones. |
| `logistic_regression_balanced` | Modelo lineal | Pipeline con preprocessing y `class_weight='balanced'` | 0.6949 | 0.6870 | 0.0079 | 0.8604 | Baseline valido: supera al dummy y cumple overfitting, pero queda por debajo del Champion. |
| `rf_depth16_leaf8_split16` | Random Forest | `n_estimators=200`, `max_depth=16`, `min_samples_leaf=8`, `min_samples_split=16`, `class_weight='balanced_subsample'` | 0.8284 | 0.8042 | 0.0242 | 0.9347 | Challenger descartado: buen rendimiento, pero inferior al mejor Random Forest. |
| `rf_depth20_leaf8_split16` | Random Forest | `n_estimators=200`, `max_depth=20`, `min_samples_leaf=8`, `min_samples_split=16`, `class_weight='balanced_subsample'` | 0.8393 | 0.8092 | 0.0301 | 0.9370 | Challenger descartado: muy competitivo, pero no mejora el F1 del Champion. |
| `rf_depth18_leaf6_split12` | Random Forest | `n_estimators=200`, `max_depth=18`, `min_samples_leaf=6`, `min_samples_split=12`, `class_weight='balanced_subsample'` | 0.8450 | 0.8105 | 0.0345 | 0.9391 | Seleccionado como Champion: mejor F1 de validacion manteniendo gap inferior a 0.05. |

Decision final:

- Se descarta el dummy porque no detecta la clase `Canceled`.
- Se conserva Logistic Regression como baseline interpretable y reproducible.
- Se promociona Random Forest `rf_depth18_leaf6_split12` como Champion por mejorar F1, precision, recall y ROC-AUC frente al baseline, manteniendo overfitting bajo el limite del proyecto.
- La tabla completa de tuning queda exportada en `reports/random_forest_tuning_results.csv`.

## Interpretabilidad y analisis de errores

### Modelo analizado

Esta seccion analiza el Champion productivizado en la API:

- Modelo: `RandomForestClassifier`.
- Artefacto: `models/champion/random_forest_champion.pkl`.
- Version: `random_forest_champion_v0.1.0`.
- Clase positiva: `Canceled`.
- Split analizado: validacion.

### Figuras de validacion

- Matriz de confusion: `reports/figures/champion_random_forest_confusion_matrix.png`.
- Curva ROC: `reports/figures/champion_random_forest_roc_curve.png`.
- Feature importance: `reports/figures/champion_random_forest_feature_importance.png`.

### Feature importance

Para Random Forest se usa `feature_importances_`, que reparte importancia entre las variables usadas por los arboles. Es una lectura global del modelo: indica que variables ayudan mas a separar cancelaciones de no cancelaciones, pero no prueba causalidad.

| feature | importance | share_percent |
| --- | --- | --- |
| lead_time | 0.3412 | 34.12 |
| no_of_special_requests | 0.1669 | 16.69 |
| avg_price_per_room | 0.1146 | 11.46 |
| arrival_month | 0.0729 | 7.29 |
| market_segment_type_Online | 0.0462 | 4.62 |
| arrival_date | 0.044 | 4.4 |
| arrival_year | 0.0402 | 4.02 |
| no_of_week_nights | 0.0285 | 2.85 |
| no_of_weekend_nights | 0.0264 | 2.64 |
| market_segment_type_Offline | 0.0263 | 2.63 |
| no_of_adults | 0.0178 | 1.78 |
| type_of_meal_plan_Meal Plan 2 | 0.013 | 1.3 |

Lectura:

- `lead_time` mantiene una de las senales mas fuertes: reservas hechas con mucha antelacion suelen tener mayor riesgo de cancelacion.
- `no_of_special_requests` aporta mucha senal: cuando hay pocas o ninguna solicitud especial, el riesgo historico de cancelacion tiende a subir.
- `market_segment_type` y variables de historial de reserva tambien ayudan a diferenciar patrones de cancelacion.

### Analisis de errores

| tipo_error | cantidad | lectura |
| --- | --- | --- |
| false_positive | 348 | Reservas que el modelo marca como riesgo de cancelacion, pero finalmente no se cancelan. |
| false_negative | 331 | Reservas que el modelo no marca como riesgo, pero finalmente se cancelan. |

Tasas sobre validacion:

- False positive rate sobre `Not_Canceled`: 0.0951.
- False negative rate sobre `Canceled`: 0.1856.

Interpretacion de negocio:

- Los falsos positivos pueden generar acciones comerciales innecesarias, pero suelen ser menos costosos que perder una cancelacion real no anticipada.
- Los falsos negativos son mas sensibles para negocio porque representan cancelaciones que no se detectaron a tiempo.
- El Champion reduce errores frente al baseline y mantiene el gap de overfitting bajo el limite operativo de 0.05.

### Limitaciones y siguientes mejoras

- El test split se evaluo una unica vez; cualquier modelo posterior necesitara datos futuros o un nuevo protocolo independiente.
- La importancia de variables es global; para explicar casos individuales convendria anadir explicabilidad local en una fase posterior.
- Como siguiente mejora, el equipo puede ajustar el umbral de decision si quiere priorizar mas recall de `Canceled` o mas precision de las alertas.

## Experimentos de Nivel Experto

### Red neuronal Challenger

Se entreno un `MLPClassifier` con capas `(64, 32)`, activacion ReLU, optimizador Adam, parada temprana y pesos de muestra balanceados. El experimento reutiliza train y validacion, pero no abre de nuevo el holdout final.

| metrica | train | validacion |
| --- | ---: | ---: |
| F1 `Canceled` | 0.8157 | 0.7742 |
| Recall `Canceled` | 0.8672 | 0.8132 |
| ROC-AUC | 0.9456 | 0.9193 |

- Gap F1 train-validacion: `0.0416`, inferior al limite `0.05`.
- Diferencia F1 frente al Champion en validacion: `-0.0363`.
- Decision: conservar `random_forest_champion_v0.1.0`.
- Evidencia: `reports/neural_network_experiment.json`.

### A/B Testing offline

El protocolo asigna de forma estratificada y reproducible el 80% de validacion al Champion y el 20% al MLP. Cada fila pertenece a un unico brazo y el holdout final permanece cerrado.

| brazo | modelo | filas | F1 `Canceled` |
| --- | --- | ---: | ---: |
| A | Champion Random Forest | 4353 | 0.8113 |
| B | Challenger MLP | 1089 | 0.7858 |

- Diferencia Challenger-Champion: `-0.0255`.
- Intervalo bootstrap del 95%: `[-0.0620, 0.0135]`.
- Victoria del Challenger estadisticamente respaldada: no.
- Decision: conservar el Champion.
- Evidencia: `reports/offline_ab_test_results.json` y `reports/offline_ab_test_assignments.csv`.

### Promocion condicionada

La politica `conditional_promotion_v1` exige artefacto compatible y cargable, mejora absoluta F1 minima `+0.02`, gap inferior a `0.05`, degradacion maxima de precision o recall `0.02` y limite inferior del intervalo A/B superior a `0`.

El MLP no es elegible: falla los gates de mejora F1, degradacion de metricas criticas y victoria A/B. Data Drift nunca puede promover un modelo; aplicar una promocion exige `--apply` y crea una copia de seguridad del Champion.

Evidencia: `reports/conditional_promotion_decision.json`. Los tres experimentos se exponen en `GET /monitoring/experiments` y se visualizan en `/monitoring`.
