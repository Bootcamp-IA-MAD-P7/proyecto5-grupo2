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
