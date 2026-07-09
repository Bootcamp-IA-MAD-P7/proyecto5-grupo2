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

### Configuracion del challenger

- Modelo: `RandomForestClassifier`.
- Preprocessing: mismo contrato de features que el baseline, con One-Hot Encoding para categoricas y sin escalado numerico porque el modelo es de arboles.
- Hiperparametros iniciales: `n_estimators=200`, `max_depth=14`, `min_samples_leaf=12`, `min_samples_split=24`, `class_weight="balanced_subsample"`.
- Clase positiva: `Canceled`.
- El test sigue reservado para evaluacion final.

### Comparacion train/validacion

| model_name | split | accuracy | precision_canceled | recall_canceled | f1_canceled | roc_auc | true_negative | false_positive | false_negative | true_positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dummy_most_frequent | train | 0.6724 | 0.0 | 0.0 | 0.0 | 0.5 | 17072 | 0 | 8319 | 0 |
| dummy_most_frequent | validation | 0.6724 | 0.0 | 0.0 | 0.0 | 0.5 | 3659 | 0 | 1783 | 0 |
| logistic_regression_balanced | train | 0.7793 | 0.635 | 0.7673 | 0.6949 | 0.8624 | 13403 | 3669 | 1936 | 6383 |
| logistic_regression_balanced | validation | 0.7732 | 0.6271 | 0.7594 | 0.687 | 0.8604 | 2854 | 805 | 429 | 1354 |
| random_forest_challenger | train | 0.8765 | 0.8042 | 0.8238 | 0.8138 | 0.9477 | 15403 | 1669 | 1466 | 6853 |
| random_forest_challenger | validation | 0.8648 | 0.7891 | 0.8015 | 0.7952 | 0.9287 | 3277 | 382 | 354 | 1429 |

### Revision de overfitting

| model_name | train | validation | absolute_gap | passes_under_5_percent_rule |
| --- | --- | --- | --- | --- |
| dummy_most_frequent | 0.0 | 0.0 | 0.0 | True |
| logistic_regression_balanced | 0.6949 | 0.687 | 0.0079 | True |
| random_forest_challenger | 0.8138 | 0.7952 | 0.0186 | True |

### Validacion cruzada del challenger

| model_name | metric | cv_mean | cv_std | cv_splits |
| --- | --- | --- | --- | --- |
| random_forest_challenger | f1_canceled | 0.799 | 0.0034 | 3 |
| random_forest_challenger | precision_canceled | 0.7854 | 0.002 | 3 |
| random_forest_challenger | recall_canceled | 0.8131 | 0.0079 | 3 |
| random_forest_challenger | roc_auc | 0.9332 | 0.002 | 3 |

### Lectura tecnica

- El Random Forest mejora el F1-score de validacion de `Canceled` de 0.6870 a 0.7952.
- El gap train-validacion del challenger es 0.0186, por debajo del limite operativo de 0.05.
- La validacion cruzada de 3 folds muestra F1 medio de 0.7990.
- Este modelo queda como challenger fuerte, pero no se selecciona Champion todavia porque falta tuning controlado y revision final contra los criterios de `T-3.4`.
