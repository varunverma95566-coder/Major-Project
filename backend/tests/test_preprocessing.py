import os
import tempfile
import numpy as np
import pandas as pd
import pytest
from app.datasets.preprocessor import FlowPreprocessor
from app.datasets.common_schema import LABEL_BENIGN

def test_preprocessor_fit_transform_consistency():
    df = pd.DataFrame({
        "flow_duration": [10.0, 50.0, 100.0, 200.0],
        "fwd_pkts": [1.0, 5.0, 10.0, 20.0],
        "bwd_pkts": [0.0, 2.0, 8.0, 15.0],
        "fwd_bytes": [60.0, 300.0, 600.0, 1200.0],
        "bwd_bytes": [0.0, 100.0, 500.0, 1000.0],
        "flow_rate_bytes_per_sec": [6.0, 8.0, 11.0, 11.0],
        "flow_rate_pkts_per_sec": [0.1, 0.14, 0.18, 0.17],
        "pkt_len_mean": [60.0, 57.0, 61.0, 62.0],
        "pkt_len_std": [0.0, 10.0, 15.0, 20.0],
        "pkt_len_max": [60.0, 100.0, 200.0, 300.0],
        "pkt_len_min": [60.0, 40.0, 40.0, 40.0],
        "fwd_pkt_len_mean": [60.0, 60.0, 60.0, 60.0],
        "bwd_pkt_len_mean": [0.0, 50.0, 62.5, 66.6],
        "iat_mean": [10.0, 7.1, 5.5, 5.7],
        "iat_std": [0.0, 3.0, 2.0, 2.5],
        "iat_max": [10.0, 50.0, 100.0, 200.0],
        "tcp_flags_syn": [1.0, 0.0, 0.0, 0.0],
        "tcp_flags_ack": [0.0, 1.0, 1.0, 1.0],
        "tcp_flags_fin": [0.0, 0.0, 0.0, 1.0],
        "tcp_flags_rst": [0.0, 0.0, 0.0, 0.0],
        "protocol": ["TCP", "TCP", "UDP", "TCP"],
        "dst_port_category": ["web", "web", "dns", "other"]
    })
    y_bin = pd.Series([0, 1, 0, 1])
    y_multi = pd.Series([LABEL_BENIGN, "DoS", LABEL_BENIGN, "PortScan"])

    prep = FlowPreprocessor()
    prep.fit(df, y_multi)

    assert prep.fitted is True
    assert prep.num_classes == 3  # Benign, DoS, PortScan

    X_num, X_cat = prep.transform(df)
    assert X_num.shape == (4, 20)
    assert X_cat.shape == (4, 2)

    # Test serialization and reloading
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        prep.save(tmp_path)
        reloaded = FlowPreprocessor.load(tmp_path)
        assert reloaded.fitted is True
        assert reloaded.num_classes == 3
        X_num_rel, X_cat_rel = reloaded.transform(df)
        np.testing.assert_allclose(X_num, X_num_rel, rtol=1e-5)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
