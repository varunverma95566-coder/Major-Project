"""Dataset Preprocessor and Artifact Serializer.

Fits scalers and encoders on training data only to prevent data leakage.
Exports and reloads preprocessing state for consistent inference.
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler
from app.datasets.common_schema import (
    STANDARD_NUMERIC_FEATURES,
    STANDARD_CATEGORICAL_FEATURES,
    LABEL_BENIGN
)


class FlowPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.numerical_features: List[str] = STANDARD_NUMERIC_FEATURES.copy()
        self.categorical_features: List[str] = STANDARD_CATEGORICAL_FEATURES.copy()
        self.category_maps: Dict[str, Dict[str, int]] = {}
        self.target_class_to_idx: Dict[str, int] = {LABEL_BENIGN: 0}
        self.idx_to_target_class: Dict[int, str] = {0: LABEL_BENIGN}
        self.fitted: bool = False
        self.num_classes: int = 1
        self.class_weights: Optional[List[float]] = None

    def fit(self, X: pd.DataFrame, y_multiclass: pd.Series) -> "FlowPreprocessor":
        # 1. Fit numerical scaler
        X_num = X[self.numerical_features].values
        self.scaler.fit(X_num)

        # 2. Fit categorical encoders
        for cat_col in self.categorical_features:
            unique_vals = sorted(X[cat_col].astype(str).unique().tolist())
            val_map = {val: idx + 1 for idx, val in enumerate(unique_vals)}
            val_map["<UNK>"] = 0  # Unknown token mapping
            self.category_maps[cat_col] = val_map

        # 3. Fit target class mapping
        unique_classes = [c for c in sorted(y_multiclass.unique().tolist()) if c != LABEL_BENIGN]
        all_classes = [LABEL_BENIGN] + unique_classes
        self.target_class_to_idx = {cls_name: i for i, cls_name in enumerate(all_classes)}
        self.idx_to_target_class = {i: cls_name for i, cls_name in enumerate(all_classes)}
        self.num_classes = len(all_classes)

        # 4. Compute balanced class weights for training
        counts = y_multiclass.value_counts()
        total_samples = len(y_multiclass)
        weights = []
        for i in range(self.num_classes):
            cname = self.idx_to_target_class[i]
            count = counts.get(cname, 1)
            # Inverse frequency weighting
            w = total_samples / (self.num_classes * count)
            weights.append(float(w))
        self.class_weights = weights

        self.fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        if not self.fitted:
            raise RuntimeError("FlowPreprocessor must be fitted before calling transform.")

        # Transform numerics
        X_num = X[self.numerical_features].values
        X_num_scaled = self.scaler.transform(X_num)

        # Transform categoricals
        cat_arrays = []
        for cat_col in self.categorical_features:
            val_map = self.category_maps.get(cat_col, {})
            encoded = X[cat_col].astype(str).map(lambda v: val_map.get(v, 0)).values
            cat_arrays.append(encoded)

        X_cat = np.column_stack(cat_arrays) if cat_arrays else np.zeros((len(X), 0), dtype=int)
        return X_num_scaled.astype(np.float32), X_cat.astype(np.int64)

    def transform_labels(self, y_binary: pd.Series, y_multiclass: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        y_bin = y_binary.values.astype(np.float32)
        y_multi = y_multiclass.map(lambda c: self.target_class_to_idx.get(str(c), 0)).values.astype(np.int64)
        return y_bin, y_multi

    def save(self, filepath: str) -> None:
        state = {
            "numerical_features": self.numerical_features,
            "categorical_features": self.categorical_features,
            "category_maps": self.category_maps,
            "target_class_to_idx": self.target_class_to_idx,
            "idx_to_target_class": {str(k): v for k, v in self.idx_to_target_class.items()},
            "num_classes": self.num_classes,
            "class_weights": self.class_weights,
            "scaler_mean": self.scaler.mean_.tolist() if hasattr(self.scaler, "mean_") else None,
            "scaler_scale": self.scaler.scale_.tolist() if hasattr(self.scaler, "scale_") else None,
        }
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "FlowPreprocessor":
        with open(filepath, "r") as f:
            state = json.load(f)
        
        preprocessor = cls()
        preprocessor.numerical_features = state["numerical_features"]
        preprocessor.categorical_features = state["categorical_features"]
        preprocessor.category_maps = state["category_maps"]
        preprocessor.target_class_to_idx = state["target_class_to_idx"]
        preprocessor.idx_to_target_class = {int(k): v for k, v in state["idx_to_target_class"].items()}
        preprocessor.num_classes = state["num_classes"]
        preprocessor.class_weights = state["class_weights"]
        
        preprocessor.scaler = StandardScaler()
        if state["scaler_mean"] is not None and state["scaler_scale"] is not None:
            preprocessor.scaler.mean_ = np.array(state["scaler_mean"], dtype=np.float64)
            preprocessor.scaler.scale_ = np.array(state["scaler_scale"], dtype=np.float64)
            preprocessor.scaler.var_ = preprocessor.scaler.scale_ ** 2
            preprocessor.scaler.n_features_in_ = len(state["scaler_mean"])

        preprocessor.fitted = True
        return preprocessor
