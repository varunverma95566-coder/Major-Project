"""Tests for BigFlow-NIDS-V2 Data Loader, Adapter, and Transformer Integration."""

import os
import pytest
import numpy as np
import pandas as pd
import torch

from app.core.config import settings
from app.datasets.bigflow_loader import BigFlowDataLoader, REQUIRED_BIGFLOW_COLUMNS
from app.datasets.adapters import detect_adapter, BigFlow_NIDS_Adapter
from app.datasets.preprocessor import FlowPreprocessor
from app.ml.flow_transformer import FlowTransformer
from app.ml.inference import ModelInferenceService


def test_bigflow_discovery():
    loader = BigFlowDataLoader(settings.BIGFLOW_NIDS_PARQUET_DIR)
    summary = loader.get_dataset_summary()
    assert summary["status"] == "ready"
    assert summary["total_files"] == 67
    assert summary["total_rows"] == 66935021
    assert len(summary["columns"]) == 55


def test_bigflow_schema_validation():
    loader = BigFlowDataLoader(settings.BIGFLOW_NIDS_PARQUET_DIR)
    summary = loader.get_dataset_summary()
    col_names = [c["name"] for c in summary["columns"]]
    is_valid, missing = loader.validate_schema(col_names)
    assert is_valid is True
    assert len(missing) == 0


def test_bigflow_adapter_detection():
    loader = BigFlowDataLoader(settings.BIGFLOW_NIDS_PARQUET_DIR)
    sample_df = loader.load_stratified_sample(sample_size=100, random_state=42)
    adapter = detect_adapter(list(sample_df.columns))
    assert isinstance(adapter, BigFlow_NIDS_Adapter)
    assert adapter.name == "BigFlow-NIDS-V2"


def test_bigflow_adaptation_and_labels():
    loader = BigFlowDataLoader(settings.BIGFLOW_NIDS_PARQUET_DIR)
    sample_df = loader.load_stratified_sample(sample_size=200, random_state=42)
    adapter = BigFlow_NIDS_Adapter()
    features_df, metadata_df, y_bin, y_multi = adapter.adapt(sample_df)

    # Check features
    assert len(features_df) == len(sample_df)
    assert "flow_duration" in features_df.columns
    assert "flow_rate_bytes_per_sec" in features_df.columns
    assert "fwd_pkts" in features_df.columns
    assert not features_df.isna().any().any()

    # Check metadata
    assert "src_ip" in metadata_df.columns
    assert "dst_ip" in metadata_df.columns
    assert "dst_port" in metadata_df.columns

    # Check labels
    assert set(y_bin.unique()).issubset({0, 1})
    assert len(y_multi) == len(sample_df)
    assert "Benign" in y_multi.values


def test_bigflow_preprocessor_and_transformer_pass():
    loader = BigFlowDataLoader(settings.BIGFLOW_NIDS_PARQUET_DIR)
    sample_df = loader.load_stratified_sample(sample_size=300, random_state=42)
    adapter = BigFlow_NIDS_Adapter()
    features_df, _, y_bin, y_multi = adapter.adapt(sample_df)

    preprocessor = FlowPreprocessor()
    preprocessor.fit(features_df, y_multi)

    X_num, X_cat = preprocessor.transform(features_df)
    y_b, y_m = preprocessor.transform_labels(y_bin, y_multi)

    assert X_num.shape[0] == 300
    assert X_num.shape[1] == len(preprocessor.numerical_features)
    assert not np.isnan(X_num).any()

    # Forward pass in FlowTransformer
    cat_cardinalities = [len(preprocessor.category_maps[c]) for c in preprocessor.categorical_features]
    model = FlowTransformer(
        num_numerical=len(preprocessor.numerical_features),
        cat_cardinalities=cat_cardinalities,
        num_classes=preprocessor.num_classes,
        embedding_dim=32,
        num_heads=2,
        num_layers=1
    )

    t_num = torch.tensor(X_num, dtype=torch.float32)
    t_cat = torch.tensor(X_cat, dtype=torch.long)
    bin_logits, multi_logits = model(t_num, t_cat)

    assert bin_logits.shape == (300,)
    assert multi_logits.shape == (300, preprocessor.num_classes)
