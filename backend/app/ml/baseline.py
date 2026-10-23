"""Baseline Random Forest Classifier for NIDS Comparison.

Provides empirical benchmark evaluation to compare against the FlowTransformer.
"""

from typing import Dict, Any, Tuple
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from app.ml.evaluation import compute_classification_metrics


class BaselineClassifier:
    def __init__(self, n_estimators: int = 100, max_depth: int = 15, random_state: int = 42):
        self.binary_model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )
        self.multiclass_model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )
        self.fitted = False

    def fit(self, X: np.ndarray, y_binary: np.ndarray, y_multiclass: np.ndarray) -> "BaselineClassifier":
        self.binary_model.fit(X, y_binary)
        self.multiclass_model.fit(X, y_multiclass)
        self.fitted = True
        return self

    def evaluate(self, X_test: np.ndarray, y_bin_test: np.ndarray, y_multi_test: np.ndarray, class_names: list) -> Dict[str, Any]:
        if not self.fitted:
            raise RuntimeError("BaselineClassifier must be fitted before evaluation.")
        
        y_bin_pred = self.binary_model.predict(X_test)
        y_multi_pred = self.multiclass_model.predict(X_test)
        
        metrics = compute_classification_metrics(
            y_true=y_multi_test,
            y_pred=y_multi_pred,
            class_names=class_names
        )
        metrics["binary_accuracy"] = float(np.mean(y_bin_pred == y_bin_test))
        return metrics
