"""FlowTransformer Training Pipeline.

Orchestrates train/val/test splitting, training-only preprocessing fitting,
mini-batch PyTorch training loop with combined classification loss,
validation tracking, baseline comparison, and artifact serialization.
"""

import os
import json
import time
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from sklearn.model_selection import train_test_split

from app.core.config import settings
from app.core.logging import logger
from app.datasets.adapters import detect_adapter
from app.datasets.bigflow_loader import BigFlowDataLoader
from app.datasets.preprocessor import FlowPreprocessor
from app.ml.flow_transformer import FlowTransformer
from app.ml.baseline import BaselineClassifier
from app.ml.evaluation import compute_classification_metrics


def train_flow_transformer_pipeline(
    dataset_path: str,
    model_name: str,
    epochs: int = 5,
    batch_size: int = 64,
    learning_rate: float = 0.001,
    train_baseline: bool = True,
    architecture_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    arch = architecture_config or {}
    embedding_dim = arch.get("embedding_dim", settings.DEFAULT_EMBEDDING_DIM)
    num_heads = arch.get("num_heads", settings.DEFAULT_NUM_HEADS)
    num_layers = arch.get("num_layers", settings.DEFAULT_NUM_LAYERS)
    dropout = arch.get("dropout", settings.DEFAULT_DROPOUT)
    feedforward_dim = arch.get("feedforward_dim", 128)
    sample_size = arch.get("sample_size", settings.DEFAULT_TRAIN_SAMPLE_SIZE)

    logger.info(f"Starting training pipeline for model '{model_name}' on dataset '{dataset_path}'")
    
    # 1. Load dataset & adapt (supporting Parquet partitions, CSV, and samples)
    if not os.path.isabs(dataset_path) and not os.path.exists(dataset_path):
        candidate = os.path.join(settings.BASE_DIR, dataset_path)
        if os.path.exists(candidate):
            dataset_path = candidate

    is_parquet_dir = os.path.isdir(dataset_path)
    is_parquet_file = os.path.isfile(dataset_path) and dataset_path.endswith(".parquet")
    is_large_csv = os.path.isfile(dataset_path) and dataset_path.endswith(".csv") and os.path.getsize(dataset_path) > 200 * 1024 * 1024

    if is_parquet_dir or is_parquet_file or is_large_csv:
        logger.info(f"Using BigFlowDataLoader for {dataset_path} (sampling up to {sample_size:,} records)")
        loader = BigFlowDataLoader(dataset_path)
        df_raw = loader.load_stratified_sample(sample_size=sample_size, random_state=42)
    else:
        logger.info(f"Loading dataset from file: {dataset_path}")
        df_raw = pd.read_csv(dataset_path)
        if len(df_raw) > sample_size:
            df_raw = df_raw.sample(n=sample_size, random_state=42).reset_index(drop=True)

    adapter = detect_adapter(list(df_raw.columns))
    logger.info(f"Detected dataset adapter: {adapter.name} for {len(df_raw):,} records")
    X_df, metadata_df, y_bin_series, y_multi_series = adapter.adapt(df_raw)

    # 2. Reproducible splits (70% train, 15% val, 15% test)
    indices = np.arange(len(X_df))

    # Safe stratification check
    stratify_main = None
    if y_multi_series.nunique() > 1 and y_multi_series.value_counts().min() >= 2:
        stratify_main = y_multi_series
    elif y_bin_series.nunique() > 1 and y_bin_series.value_counts().min() >= 2:
        stratify_main = y_bin_series

    train_idx, temp_idx = train_test_split(indices, test_size=0.30, random_state=42, stratify=stratify_main)

    temp_multi = y_multi_series.iloc[temp_idx]
    temp_bin = y_bin_series.iloc[temp_idx]
    stratify_val = None
    if temp_multi.nunique() > 1 and temp_multi.value_counts().min() >= 2:
        stratify_val = temp_multi
    elif temp_bin.nunique() > 1 and temp_bin.value_counts().min() >= 2:
        stratify_val = temp_bin

    val_idx, test_idx = train_test_split(temp_idx, test_size=0.50, random_state=42, stratify=stratify_val)

    X_train_df = X_df.iloc[train_idx].reset_index(drop=True)
    y_bin_train = y_bin_series.iloc[train_idx].reset_index(drop=True)
    y_multi_train = y_multi_series.iloc[train_idx].reset_index(drop=True)

    X_val_df = X_df.iloc[val_idx].reset_index(drop=True)
    y_bin_val = y_bin_series.iloc[val_idx].reset_index(drop=True)
    y_multi_val = y_multi_series.iloc[val_idx].reset_index(drop=True)

    X_test_df = X_df.iloc[test_idx].reset_index(drop=True)
    y_bin_test = y_bin_series.iloc[test_idx].reset_index(drop=True)
    y_multi_test = y_multi_series.iloc[test_idx].reset_index(drop=True)

    # 3. Fit preprocessor on training data only
    preprocessor = FlowPreprocessor()
    preprocessor.fit(X_train_df, y_multi_train)

    X_num_train, X_cat_train = preprocessor.transform(X_train_df)
    y_b_train, y_m_train = preprocessor.transform_labels(y_bin_train, y_multi_train)

    X_num_val, X_cat_val = preprocessor.transform(X_val_df)
    y_b_val, y_m_val = preprocessor.transform_labels(y_bin_val, y_multi_val)

    X_num_test, X_cat_test = preprocessor.transform(X_test_df)
    y_b_test, y_m_test = preprocessor.transform_labels(y_bin_test, y_multi_test)

    # 4. PyTorch DataLoaders
    train_dataset = TensorDataset(
        torch.tensor(X_num_train, dtype=torch.float32),
        torch.tensor(X_cat_train, dtype=torch.long),
        torch.tensor(y_b_train, dtype=torch.float32),
        torch.tensor(y_m_train, dtype=torch.long)
    )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # 5. Initialize Model
    cat_cardinalities = [len(preprocessor.category_maps[c]) for c in preprocessor.categorical_features]
    model = FlowTransformer(
        num_numerical=len(preprocessor.numerical_features),
        cat_cardinalities=cat_cardinalities,
        num_classes=preprocessor.num_classes,
        embedding_dim=embedding_dim,
        num_heads=num_heads,
        num_layers=num_layers,
        feedforward_dim=feedforward_dim,
        dropout=dropout
    )

    # 6. Loss & Optimizer
    criterion_bin = nn.BCEWithLogitsLoss()
    weights_tensor = torch.tensor(preprocessor.class_weights, dtype=torch.float32)
    criterion_multi = nn.CrossEntropyLoss(weight=weights_tensor)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)

    # 7. Training Loop
    history = {"train_loss": [], "val_loss": [], "val_accuracy": []}
    logger.info(f"Training for {epochs} epochs...")

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for num_b, cat_b, y_bin_b, y_mul_b in train_loader:
            optimizer.zero_grad()
            logits_bin, logits_mul = model(num_b, cat_b)
            loss_b = criterion_bin(logits_bin, y_bin_b)
            loss_m = criterion_multi(logits_mul, y_mul_b)
            loss = loss_b + loss_m
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_train_loss = total_loss / max(len(train_loader), 1)

        # Validation step
        model.eval()
        with torch.no_grad():
            t_num_val = torch.tensor(X_num_val, dtype=torch.float32)
            t_cat_val = torch.tensor(X_cat_val, dtype=torch.long)
            v_logits_bin, v_logits_mul = model(t_num_val, t_cat_val)
            v_loss = (criterion_bin(v_logits_bin, torch.tensor(y_b_val, dtype=torch.float32)) +
                      criterion_multi(v_logits_mul, torch.tensor(y_m_val, dtype=torch.long))).item()
            v_pred = torch.argmax(v_logits_mul, dim=-1).numpy()
            v_acc = float(np.mean(v_pred == y_m_val))

        history["train_loss"].append(round(avg_train_loss, 4))
        history["val_loss"].append(round(v_loss, 4))
        history["val_accuracy"].append(round(v_acc, 4))
        logger.info(f"Epoch {epoch}/{epochs} - Train Loss: {avg_train_loss:.4f} - Val Loss: {v_loss:.4f} - Val Acc: {v_acc:.4f}")

    # 8. Evaluation on Held-Out Test Set
    model.eval()
    with torch.no_grad():
        t_num_test = torch.tensor(X_num_test, dtype=torch.float32)
        t_cat_test = torch.tensor(X_cat_test, dtype=torch.long)
        _, test_logits_mul = model(t_num_test, t_cat_test)
        test_preds = torch.argmax(test_logits_mul, dim=-1).numpy()

    class_names = [preprocessor.idx_to_target_class[i] for i in range(preprocessor.num_classes)]
    transformer_metrics = compute_classification_metrics(y_m_test, test_preds, class_names)

    # 9. Baseline Comparison Model
    baseline_metrics = {}
    if train_baseline:
        logger.info("Fitting Baseline Random Forest Classifier for empirical comparison...")
        baseline = BaselineClassifier()
        # Combine numerical & categorical for baseline tabular model
        X_train_combined = np.hstack([X_num_train, X_cat_train])
        X_test_combined = np.hstack([X_num_test, X_cat_test])
        baseline.fit(X_train_combined, y_b_train, y_m_train)
        baseline_metrics = baseline.evaluate(X_test_combined, y_b_test, y_m_test, class_names)
        logger.info(f"Baseline F1: {baseline_metrics['f1_score']:.4f} vs FlowTransformer F1: {transformer_metrics['f1_score']:.4f}")

    # 10. Save Artifacts
    model_dir = os.path.join(settings.ARTIFACTS_DIR, model_name)
    os.makedirs(model_dir, exist_ok=True)
    
    weights_path = os.path.join(model_dir, "weights.pt")
    torch.save(model.state_dict(), weights_path)

    preprocessor_path = os.path.join(model_dir, "preprocessor.json")
    preprocessor.save(preprocessor_path)

    metadata_path = os.path.join(model_dir, "metadata.json")
    meta = {
        "model_name": model_name,
        "model_type": "FlowTransformer",
        "created_at": time.time(),
        "architecture_config": {
            "embedding_dim": embedding_dim,
            "num_heads": num_heads,
            "num_layers": num_layers,
            "dropout": dropout,
            "feedforward_dim": feedforward_dim,
            "num_numerical": len(preprocessor.numerical_features),
            "cat_cardinalities": cat_cardinalities,
            "num_classes": preprocessor.num_classes
        },
        "target_classes": class_names,
        "metrics": transformer_metrics,
        "baseline_metrics": baseline_metrics,
        "history": history,
        "weights_path": weights_path,
        "preprocessor_path": preprocessor_path
    }
    with open(metadata_path, "w") as f:
        json.dump(meta, f, indent=2)

    logger.info(f"Model artifacts saved successfully in {model_dir}")
    return meta
