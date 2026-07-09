"""Classification metrics used by model training scripts."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


POSITIVE_LABEL = 1


@dataclass(frozen=True)
class ClassificationMetrics:
    """Metrics for one model on one data split."""

    model_name: str
    split: str
    accuracy: float
    precision_canceled: float
    recall_canceled: float
    f1_canceled: float
    roc_auc: float | None
    true_negative: int
    false_positive: int
    false_negative: int
    true_positive: int


def evaluate_classification(
    *,
    model_name: str,
    split: str,
    y_true,
    y_pred,
    y_score=None,
) -> ClassificationMetrics:
    """Calculate the required binary classification metrics."""

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    roc_auc = None
    if y_score is not None:
        roc_auc = roc_auc_score(y_true, y_score)

    return ClassificationMetrics(
        model_name=model_name,
        split=split,
        accuracy=accuracy_score(y_true, y_pred),
        precision_canceled=precision_score(
            y_true,
            y_pred,
            pos_label=POSITIVE_LABEL,
            zero_division=0,
        ),
        recall_canceled=recall_score(
            y_true,
            y_pred,
            pos_label=POSITIVE_LABEL,
            zero_division=0,
        ),
        f1_canceled=f1_score(
            y_true,
            y_pred,
            pos_label=POSITIVE_LABEL,
            zero_division=0,
        ),
        roc_auc=roc_auc,
        true_negative=int(tn),
        false_positive=int(fp),
        false_negative=int(fn),
        true_positive=int(tp),
    )


def metrics_to_dataframe(metrics: list[ClassificationMetrics]) -> pd.DataFrame:
    """Convert metric objects into a dataframe for reports."""

    return pd.DataFrame([asdict(metric) for metric in metrics])
