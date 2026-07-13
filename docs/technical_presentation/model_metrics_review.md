# Revision final de metricas y overfitting - T-6.2

Responsable principal: Integrante 1 - ML Core  
Fecha de revision: 2026-07-13

## Alcance

Esta revision valida que el modelo final del proyecto sea coherente entre codigo, artefactos y documentacion tecnica. No modifica `.specify`.

## Modelo final revisado

- Champion: `random_forest_champion_v0.1.0`.
- Artefacto: `models/champion/random_forest_champion.pkl`.
- Metadata: `models/champion/champion_metadata.json`.
- API: `POST /predict` carga el Champion mediante `app/backend/services/model_service.py`.
- Clase positiva principal: `Canceled`.

## Comparacion principal

| criterio | Baseline Logistic Regression | Champion Random Forest |
| --- | --- | --- |
| F1 validacion `Canceled` | 0.6870 | 0.8105 |
| Precision validacion `Canceled` | 0.6271 | 0.8067 |
| Recall validacion `Canceled` | 0.7594 | 0.8144 |
| ROC-AUC validacion | 0.8604 | 0.9391 |
| Gap F1 train-validacion | 0.0079 | 0.0345 |
| Regla overfitting < 0.05 | Cumple | Cumple |

## Validacion cruzada del Champion

| metrica | media | desviacion | folds |
| --- | --- | --- | --- |
| F1 `Canceled` | 0.8160 | 0.0071 | 3 |
| Precision `Canceled` | 0.8101 | 0.0083 | 3 |
| Recall `Canceled` | 0.8220 | 0.0079 | 3 |
| ROC-AUC | 0.9426 | 0.0017 | 3 |

## Evidencia visual

- Matriz de confusion: `reports/figures/champion_random_forest_confusion_matrix.png`.
- Curva ROC: `reports/figures/champion_random_forest_roc_curve.png`.
- Feature importance: `reports/figures/champion_random_forest_feature_importance.png`.

## Conclusion para defensa

El Champion Random Forest mejora claramente el F1 de la clase `Canceled`, mantiene el gap de overfitting por debajo del limite del proyecto y muestra estabilidad razonable en validacion cruzada. El split de test queda reservado para una comprobacion imparcial final si el equipo decide hacer una validacion adicional antes de presentar.
