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
- El test queda reservado para una evaluacion posterior mas imparcial.

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
- Este modelo queda como challenger optimizado y candidato principal para la seleccion formal de Champion en `T-3.4`.

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
- La API todavia puede seguir cargando el baseline hasta que el equipo cierre la tarea de integracion de app; esta decision deja preparado el artefacto ML para ese cambio.

## Interpretabilidad y analisis de errores

### Modelo analizado

Esta seccion analiza el baseline productivizado en la API:

- Modelo: `logistic_regression_balanced`.
- Artefacto: `models/baseline/logistic_regression_baseline.pkl`.
- Clase positiva: `Canceled`.
- Split analizado: validacion.

### Feature importance equivalente

Para Logistic Regression se usa el valor absoluto de los coeficientes como aproximacion de importancia. Los coeficientes positivos empujan la prediccion hacia `Canceled`; los negativos empujan hacia `Not_Canceled`.

| feature | coefficient | absolute_coefficient | effect_on_canceled |
| --- | --- | --- | --- |
| repeated_guest | -2.1494 | 2.1494 | decreases_risk |
| market_segment_type_Complementary | -1.7523 | 1.7523 | decreases_risk |
| required_car_parking_space | -1.5491 | 1.5491 | decreases_risk |
| lead_time | 1.3578 | 1.3578 | increases_risk |
| no_of_special_requests | -1.1481 | 1.1481 | decreases_risk |
| room_type_reserved_Room_Type 7 | -1.1301 | 1.1301 | decreases_risk |
| market_segment_type_Aviation | 0.9868 | 0.9868 | increases_risk |
| market_segment_type_Online | 0.9308 | 0.9308 | increases_risk |
| market_segment_type_Offline | -0.8437 | 0.8437 | decreases_risk |
| no_of_previous_bookings_not_canceled | -0.8244 | 0.8244 | decreases_risk |
| avg_price_per_room | 0.6137 | 0.6137 | increases_risk |
| room_type_reserved_Room_Type 1 | 0.5055 | 0.5055 | increases_risk |

Lectura:

- `lead_time` aparece como una de las senales mas fuertes: reservas con mayor antelacion tienden a elevar el riesgo de cancelacion.
- `no_of_special_requests` tiene coeficiente negativo: mas solicitudes especiales tienden a reducir el riesgo estimado.
- Algunas categorias de `market_segment_type` y `room_type_reserved` aportan senal relevante, pero deben interpretarse como asociaciones historicas, no como causas directas.

### Analisis de errores

| tipo_error | cantidad | lectura |
| --- | --- | --- |
| false_positive | 805 | Reservas que el modelo marca como riesgo de cancelacion, pero finalmente no se cancelan. |
| false_negative | 429 | Reservas que el modelo no marca como riesgo, pero finalmente se cancelan. |

Tasas sobre validacion:

- False positive rate sobre `Not_Canceled`: 0.2200.
- False negative rate sobre `Canceled`: 0.2406.

Interpretacion de negocio:

- Los falsos positivos pueden generar acciones comerciales innecesarias, pero suelen ser menos costosos que perder una cancelacion real no anticipada.
- Los falsos negativos son mas sensibles para negocio porque representan cancelaciones que no se detectaron a tiempo.
- Como siguiente mejora, el equipo puede ajustar el umbral de decision si quiere priorizar mas recall de `Canceled` o mas precision de las alertas.

### Limitaciones y siguientes mejoras

- El baseline es funcional y cumple el Nivel Esencial, pero no es necesariamente el mejor modelo final.
- Random Forest ya muestra mejor F1 de validacion como challenger, por lo que puede evaluarse como Champion en el Nivel Medio.
- La interpretabilidad de coeficientes aplica al baseline lineal; si se promueve un modelo de arboles, conviene reportar importancias del modelo final.
