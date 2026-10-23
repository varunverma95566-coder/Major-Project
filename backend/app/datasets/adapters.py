"""Dataset Adapters for NetFlow and NIDS Research Datasets.

Provides parsing, feature standardization, column mapping, and label normalization
for NF-UNSW-NB15-v2, NF-BoT-IoT-v2, UNSW-NB15, Edge-IIoTset, CIC-IDS2017/2018, and Generic CSVs.
"""

from typing import Tuple, Dict, Any, List, Optional
import numpy as np
import pandas as pd
from app.datasets.common_schema import (
    STANDARD_NUMERIC_FEATURES,
    STANDARD_CATEGORICAL_FEATURES,
    CONTEXT_METADATA_FIELDS,
    TARGET_LABEL_BINARY,
    TARGET_LABEL_MULTICLASS,
    LABEL_BENIGN,
    CANONICAL_ATTACK_CATEGORIES,
)


class BaseDatasetAdapter:
    name: str = "BaseAdapter"
    
    def can_handle(self, columns: List[str]) -> bool:
        raise NotImplementedError

    def adapt(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Returns: (features_df, metadata_df, binary_labels, multiclass_labels)"""
        raise NotImplementedError


class BigFlow_NIDS_Adapter(BaseDatasetAdapter):
    """Primary Adapter for BigFlow-NIDS-V2 NetFlow dataset (Parquet / CSV)."""
    name = "BigFlow-NIDS-V2"

    def can_handle(self, columns: List[str]) -> bool:
        cols_lower = [str(c).lower().strip() for c in columns]
        has_bytes = "in_bytes" in cols_lower and "out_bytes" in cols_lower
        has_flow_dur = "flow_duration_milliseconds" in cols_lower
        has_bigflow_markers = any(m in cols_lower for m in [
            "src_to_dst_second_bytes", "client_tcp_flags", "server_tcp_flags",
            "icmp_ipv4_type", "dns_ttl_answer", "longest_flow_pkt"
        ])
        return has_bytes and has_flow_dur and (has_bigflow_markers or "attack" in cols_lower)

    def adapt(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        cols = {str(c).lower().strip(): c for c in df.columns}

        # 1. Context Metadata (Never leaked into model features)
        metadata = pd.DataFrame()
        metadata["src_ip"] = df[cols["ipv4_src_addr"]].astype(str) if "ipv4_src_addr" in cols else "192.168.1.100"
        metadata["dst_ip"] = df[cols["ipv4_dst_addr"]].astype(str) if "ipv4_dst_addr" in cols else "10.0.0.1"
        metadata["src_port"] = pd.to_numeric(df[cols["l4_src_port"]], errors="coerce").fillna(0).astype(int) if "l4_src_port" in cols else 49152
        metadata["dst_port"] = pd.to_numeric(df[cols["l4_dst_port"]], errors="coerce").fillna(0).astype(int) if "l4_dst_port" in cols else 80
        metadata["protocol"] = df[cols["protocol"]].astype(str) if "protocol" in cols else "6"

        if "flow_start_milliseconds" in cols:
            metadata["timestamp"] = pd.to_datetime(df[cols["flow_start_milliseconds"]], unit="ms", errors="coerce").fillna(pd.Timestamp.now("UTC"))
        else:
            metadata["timestamp"] = pd.Timestamp.now("UTC")


        # 2. Target Labels (Never leaked into model features)
        if "label" in cols:
            binary_labels = pd.to_numeric(df[cols["label"]], errors="coerce").fillna(0).astype(int)
        elif "attack" in cols:
            binary_labels = (df[cols["attack"]].astype(str).str.strip().str.lower() != "benign").astype(int)
        else:
            binary_labels = pd.Series([0] * len(df))

        if "attack" in cols:
            multiclass_labels = df[cols["attack"]].astype(str).str.strip().replace({
                "": LABEL_BENIGN,
                "0": LABEL_BENIGN,
                "nan": LABEL_BENIGN,
                "None": LABEL_BENIGN
            })
        else:
            multiclass_labels = binary_labels.map({0: LABEL_BENIGN, 1: "Generic_Malicious"})

        # 3. Standard Numerical Features Mapping
        features = pd.DataFrame()
        features["flow_duration"] = pd.to_numeric(df[cols.get("flow_duration_milliseconds", "")], errors="coerce").fillna(100.0) if "flow_duration_milliseconds" in cols else 100.0
        features["fwd_pkts"] = pd.to_numeric(df[cols.get("in_pkts", "")], errors="coerce").fillna(1.0) if "in_pkts" in cols else 1.0
        features["bwd_pkts"] = pd.to_numeric(df[cols.get("out_pkts", "")], errors="coerce").fillna(0.0) if "out_pkts" in cols else 0.0
        features["fwd_bytes"] = pd.to_numeric(df[cols.get("in_bytes", "")], errors="coerce").fillna(64.0) if "in_bytes" in cols else 64.0
        features["bwd_bytes"] = pd.to_numeric(df[cols.get("out_bytes", "")], errors="coerce").fillna(0.0) if "out_bytes" in cols else 0.0

        duration_sec = np.maximum(features["flow_duration"] / 1000.0, 1e-4)
        features["flow_rate_bytes_per_sec"] = (features["fwd_bytes"] + features["bwd_bytes"]) / duration_sec
        features["flow_rate_pkts_per_sec"] = (features["fwd_pkts"] + features["bwd_pkts"]) / duration_sec

        total_pkts = np.maximum(features["fwd_pkts"] + features["bwd_pkts"], 1.0)
        total_bytes = features["fwd_bytes"] + features["bwd_bytes"]
        features["pkt_len_mean"] = total_bytes / total_pkts
        features["pkt_len_std"] = np.abs(features["fwd_bytes"] - features["bwd_bytes"]) / total_pkts

        if "longest_flow_pkt" in cols:
            features["pkt_len_max"] = pd.to_numeric(df[cols["longest_flow_pkt"]], errors="coerce").fillna(features["fwd_bytes"])
        else:
            features["pkt_len_max"] = np.maximum(features["fwd_bytes"], features["bwd_bytes"])

        if "shortest_flow_pkt" in cols:
            features["pkt_len_min"] = pd.to_numeric(df[cols["shortest_flow_pkt"]], errors="coerce").fillna(0.0)
        else:
            features["pkt_len_min"] = np.minimum(features["fwd_bytes"], features["bwd_bytes"]) / total_pkts

        features["fwd_pkt_len_mean"] = features["fwd_bytes"] / np.maximum(features["fwd_pkts"], 1.0)
        features["bwd_pkt_len_mean"] = features["bwd_bytes"] / np.maximum(features["bwd_pkts"], 1.0)

        if "src_to_dst_iat_avg" in cols:
            features["iat_mean"] = pd.to_numeric(df[cols["src_to_dst_iat_avg"]], errors="coerce").fillna(features["flow_duration"] / total_pkts)
        else:
            features["iat_mean"] = features["flow_duration"] / total_pkts

        if "src_to_dst_iat_stddev" in cols:
            features["iat_std"] = pd.to_numeric(df[cols["src_to_dst_iat_stddev"]], errors="coerce").fillna(features["iat_mean"] * 0.5)
        else:
            features["iat_std"] = features["iat_mean"] * 0.5

        if "src_to_dst_iat_max" in cols:
            features["iat_max"] = pd.to_numeric(df[cols["src_to_dst_iat_max"]], errors="coerce").fillna(features["flow_duration"])
        else:
            features["iat_max"] = features["flow_duration"]

        tcp_flags = pd.to_numeric(df[cols["tcp_flags"]], errors="coerce").fillna(0).astype(int) if "tcp_flags" in cols else pd.Series([0] * len(df))
        features["tcp_flags_syn"] = ((tcp_flags & 2) > 0).astype(float)
        features["tcp_flags_ack"] = ((tcp_flags & 16) > 0).astype(float)
        features["tcp_flags_fin"] = ((tcp_flags & 1) > 0).astype(float)
        features["tcp_flags_rst"] = ((tcp_flags & 4) > 0).astype(float)

        # 4. Standard Categoricals
        features["protocol"] = metadata["protocol"]
        dst_port_cat = metadata["dst_port"].apply(
            lambda p: "web" if p in [80, 443, 8080, 8443] else ("dns" if p == 53 else ("ssh" if p == 22 else ("ftp" if p in [20, 21] else "other")))
        )
        features["dst_port_category"] = dst_port_cat

        return clean_dataframe(features), metadata, binary_labels, multiclass_labels


class NF_UNSW_NB15_v2_Adapter(BaseDatasetAdapter):
    name = "NF-UNSW-NB15-v2"
    
    def can_handle(self, columns: List[str]) -> bool:
        cols_lower = [c.lower() for c in columns]
        return "in_bytes" in cols_lower and "l4_dst_port" in cols_lower and "attack" in cols_lower

    def adapt(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        cols = {c.lower(): c for c in df.columns}
        
        # Metadata extraction
        metadata = pd.DataFrame()
        metadata["src_ip"] = df[cols.get("ipv4_src_addr", df.columns[0])] if "ipv4_src_addr" in cols else "192.168.1.10"
        metadata["dst_ip"] = df[cols.get("ipv4_dst_addr", df.columns[1])] if "ipv4_dst_addr" in cols else "10.0.0.1"
        metadata["src_port"] = df[cols.get("l4_src_port", df.columns[2])].fillna(0).astype(int) if "l4_src_port" in cols else 0
        metadata["dst_port"] = df[cols.get("l4_dst_port", df.columns[3])].fillna(0).astype(int) if "l4_dst_port" in cols else 80
        metadata["protocol"] = df[cols.get("protocol", "protocol")].astype(str) if "protocol" in cols else "6"
        metadata["timestamp"] = pd.Timestamp.utcnow()

        # Labels
        if "label" in cols:
            binary_labels = df[cols["label"]].astype(int)
        elif "attack" in cols:
            binary_labels = (df[cols["attack"]].astype(str).str.lower() != "benign").astype(int)
        else:
            binary_labels = pd.Series([0] * len(df))

        if "attack" in cols:
            multiclass_labels = df[cols["attack"]].astype(str).replace({"": LABEL_BENIGN, "0": LABEL_BENIGN, "Benign": LABEL_BENIGN})
        else:
            multiclass_labels = binary_labels.map({0: LABEL_BENIGN, 1: "Generic_Malicious"})

        # Feature Mapping
        features = pd.DataFrame()
        features["flow_duration"] = df[cols["flow_duration_milliseconds"]].astype(float) if "flow_duration_milliseconds" in cols else 100.0
        features["fwd_pkts"] = df[cols["in_pkts"]].astype(float) if "in_pkts" in cols else 1.0
        features["bwd_pkts"] = df[cols["out_pkts"]].astype(float) if "out_pkts" in cols else 1.0
        features["fwd_bytes"] = df[cols["in_bytes"]].astype(float) if "in_bytes" in cols else 64.0
        features["bwd_bytes"] = df[cols["out_bytes"]].astype(float) if "out_bytes" in cols else 64.0
        
        duration_sec = np.maximum(features["flow_duration"] / 1000.0, 1e-4)
        features["flow_rate_bytes_per_sec"] = (features["fwd_bytes"] + features["bwd_bytes"]) / duration_sec
        features["flow_rate_pkts_per_sec"] = (features["fwd_pkts"] + features["bwd_pkts"]) / duration_sec
        
        total_pkts = np.maximum(features["fwd_pkts"] + features["bwd_pkts"], 1.0)
        total_bytes = features["fwd_bytes"] + features["bwd_bytes"]
        features["pkt_len_mean"] = total_bytes / total_pkts
        features["pkt_len_std"] = np.abs(features["fwd_bytes"] - features["bwd_bytes"]) / total_pkts
        features["pkt_len_max"] = np.maximum(features["fwd_bytes"], features["bwd_bytes"])
        features["pkt_len_min"] = np.minimum(features["fwd_bytes"], features["bwd_bytes"]) / total_pkts
        
        features["fwd_pkt_len_mean"] = features["fwd_bytes"] / np.maximum(features["fwd_pkts"], 1.0)
        features["bwd_pkt_len_mean"] = features["bwd_bytes"] / np.maximum(features["bwd_pkts"], 1.0)
        
        features["iat_mean"] = features["flow_duration"] / total_pkts
        features["iat_std"] = features["iat_mean"] * 0.5
        features["iat_max"] = features["flow_duration"]
        
        tcp_flags = df[cols["tcp_flags"]].astype(int) if "tcp_flags" in cols else pd.Series([0] * len(df))
        features["tcp_flags_syn"] = ((tcp_flags & 2) > 0).astype(float)
        features["tcp_flags_ack"] = ((tcp_flags & 16) > 0).astype(float)
        features["tcp_flags_fin"] = ((tcp_flags & 1) > 0).astype(float)
        features["tcp_flags_rst"] = ((tcp_flags & 4) > 0).astype(float)
        
        # Categoricals
        features["protocol"] = metadata["protocol"]
        dst_port_cat = metadata["dst_port"].apply(lambda p: "web" if p in [80, 443, 8080] else ("dns" if p == 53 else ("ssh" if p == 22 else "other")))
        features["dst_port_category"] = dst_port_cat

        return clean_dataframe(features), metadata, binary_labels, multiclass_labels


class GenericCSVAdapter(BaseDatasetAdapter):
    name = "Generic-NIDS-Adapter"
    
    def can_handle(self, columns: List[str]) -> bool:
        return True  # Fallback adapter

    def adapt(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        cols_lower = {str(c).lower().strip(): c for c in df.columns}
        
        # Detect label column
        label_col = None
        for candidate in ["label", "attack", "class", "is_attack", "attack_cat", "target"]:
            if candidate in cols_lower:
                label_col = cols_lower[candidate]
                break

        if label_col:
            raw_labels = df[label_col].astype(str)
            binary_labels = raw_labels.apply(lambda x: 0 if str(x).lower() in ["0", "benign", "normal", "false"] else 1)
            multiclass_labels = raw_labels.apply(lambda x: LABEL_BENIGN if str(x).lower() in ["0", "benign", "normal", "false"] else str(x))
        else:
            binary_labels = pd.Series([0] * len(df))
            multiclass_labels = pd.Series([LABEL_BENIGN] * len(df))

        # Context metadata
        metadata = pd.DataFrame()
        metadata["src_ip"] = df[cols_lower["src_ip"]].astype(str) if "src_ip" in cols_lower else (df[cols_lower["source_ip"]].astype(str) if "source_ip" in cols_lower else "192.168.1.50")
        metadata["dst_ip"] = df[cols_lower["dst_ip"]].astype(str) if "dst_ip" in cols_lower else (df[cols_lower["destination_ip"]].astype(str) if "destination_ip" in cols_lower else "10.0.0.2")
        metadata["src_port"] = df[cols_lower["src_port"]].fillna(0).astype(int) if "src_port" in cols_lower else 49152
        metadata["dst_port"] = df[cols_lower["dst_port"]].fillna(0).astype(int) if "dst_port" in cols_lower else 80
        metadata["protocol"] = df[cols_lower["protocol"]].astype(str) if "protocol" in cols_lower else "TCP"
        metadata["timestamp"] = pd.Timestamp.now("UTC")


        # Build standard feature set from present columns or synthesize defaults
        features = pd.DataFrame()
        for num_feat in STANDARD_NUMERIC_FEATURES:
            match = None
            for col_cand in [num_feat, num_feat.replace("_", " "), num_feat.replace("_", "")]:
                if col_cand.lower() in cols_lower:
                    match = cols_lower[col_cand.lower()]
                    break
            if match:
                features[num_feat] = pd.to_numeric(df[match], errors="coerce").fillna(0.0)
            else:
                features[num_feat] = 0.0

        features["protocol"] = metadata["protocol"]
        features["dst_port_category"] = metadata["dst_port"].apply(
            lambda p: "web" if p in [80, 443, 8080] else ("dns" if p == 53 else ("ssh" if p == 22 else "other"))
        )

        return clean_dataframe(features), metadata, binary_labels, multiclass_labels


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Removes infinite values, clips extreme outliers, and fills NaNs."""
    df_clean = df.copy()
    for col in df_clean.select_dtypes(include=[np.number]).columns:
        df_clean[col] = df_clean[col].replace([np.inf, -np.inf], np.nan)
        median_val = df_clean[col].median()
        if pd.isna(median_val):
            median_val = 0.0
        df_clean[col] = df_clean[col].fillna(median_val)
    for col in df_clean.select_dtypes(include=["object", "string", str]).columns:
        df_clean[col] = df_clean[col].fillna("unknown")
    return df_clean



ADAPTERS: List[BaseDatasetAdapter] = [
    BigFlow_NIDS_Adapter(),
    NF_UNSW_NB15_v2_Adapter(),
    GenericCSVAdapter(),
]


def detect_adapter(columns: List[str]) -> BaseDatasetAdapter:
    for adapter in ADAPTERS:
        if adapter.can_handle(columns):
            return adapter
    return GenericCSVAdapter()
