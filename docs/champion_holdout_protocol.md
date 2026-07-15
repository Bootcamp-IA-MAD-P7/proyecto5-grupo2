# Protocolo de evaluación final del Champion

## Objetivo

Evaluar una única vez el Champion `random_forest_champion_v0.1.0` sobre el 15 % de test reservado desde el inicio del proyecto.

Esta evaluación estima el rendimiento final del modelo sobre datos no utilizados para entrenamiento, selección, validación cruzada ni ajuste de hiperparámetros.

## Condiciones previas

- El Champion y sus hiperparámetros permanecen congelados.
- El split se reconstruye con la función `prepare_data_splits` del contrato de preprocesamiento.
- La separación es estratificada: 70 % train, 15 % validación y 15 % test.
- El `random_state` es `42`.
- `Booking_ID` queda excluido de las variables del modelo.
- Solo `X_test` e `y_test` se utilizan para calcular las métricas finales.

## Criterios declarados antes de abrir el holdout

- F1-score de la clase `Canceled` en test igual o superior a `0.80`.
- Diferencia absoluta entre F1 de validación y F1 de test igual o inferior a `0.05`.

Las métricas informativas adicionales son accuracy, precision, recall, ROC-AUC y matriz de confusión.

## Ejecución

```bash
python -m src.evaluation.evaluate_champion_holdout
```

El comando:

1. Calcula las métricas exclusivamente sobre el test reservado.
2. Registra hashes SHA-256 del dataset y del artefacto Champion.
3. Guarda la evidencia en `reports/champion_test_metrics.json`.
4. Añade las métricas finales a `models/champion/champion_metadata.json`.
5. Rechaza una segunda ejecución cuando el resultado ya está registrado.

## Política posterior

Una vez abierto el holdout, sus resultados no se utilizarán para modificar hiperparámetros, seleccionar variables o reentrenar el Champion. Cualquier modelo posterior deberá tratarse como una nueva versión y validarse con datos futuros o con un nuevo protocolo independiente.
