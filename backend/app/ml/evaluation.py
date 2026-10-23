"""Model Evaluation and Performance Metrics Utility.

Calculates accuracy, precision, recall, F1-score, per-class breakdown,
and confusion matrix on held-out test splits.
"""

from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: List[str]
) -> Dict[str, Any]:
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    rec = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
    
    # Per-class metrics
    labels = list(range(len(class_names)))
    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=class_names,
        output_dict=True,
        zero_division=0
    )
    
    per_class = {}
    for cname in class_names:
        if cname in report:
            per_class[cname] = {
                "precision": float(report[cname]["precision"]),
                "recall": float(report[cname]["recall"]),
                "f1_score": float(report[cname]["f1-score"]),
                "support": int(report[cname]["support"])
            }

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))
    
    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "per_class_metrics": per_class,
        "confusion_matrix": cm.tolist(),
        "classes": class_names
    }
