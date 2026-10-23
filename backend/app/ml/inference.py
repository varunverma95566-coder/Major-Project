"""Model Inference Service.

Loads active FlowTransformer weights and preprocessors,
executes batched or single-flow predictions, generates confidence,
probabilities, and calls explainability attributions.
"""

import os
import json
import time
import torch
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from app.core.config import settings
from app.core.logging import logger
from app.datasets.preprocessor import FlowPreprocessor
from app.datasets.common_schema import LABEL_BENIGN
from app.ml.flow_transformer import FlowTransformer
from app.ml.explainability import compute_feature_contributions, generate_human_readable_explanation, llm_provider

# Dual-head open-set anomaly threshold:
# When binary classifier indicates malicious activity with high confidence,
# but multiclass confidence falls below this threshold or predicts Benign,
# the flow is flagged as an out-of-distribution / open-set anomaly.
OPEN_SET_THRESHOLD = 0.40


class ModelInferenceService:
    def __init__(self):
        self.active_model_name: Optional[str] = None
        self.model: Optional[FlowTransformer] = None
        self.preprocessor: Optional[FlowPreprocessor] = None
        self.metadata: Optional[Dict[str, Any]] = None

    def load_model(self, model_name: str) -> bool:
        model_dir = os.path.join(settings.ARTIFACTS_DIR, model_name)
        weights_path = os.path.join(model_dir, "weights.pt")
        prep_path = os.path.join(model_dir, "preprocessor.json")
        meta_path = os.path.join(model_dir, "metadata.json")

        if not (os.path.exists(weights_path) and os.path.exists(prep_path) and os.path.exists(meta_path)):
            logger.warning(f"Model artifacts not found for '{model_name}' in {model_dir}")
            return False

        with open(meta_path, "r") as f:
            self.metadata = json.load(f)

        self.preprocessor = FlowPreprocessor.load(prep_path)
        arch = self.metadata["architecture_config"]
        
        self.model = FlowTransformer(
            num_numerical=arch["num_numerical"],
            cat_cardinalities=arch["cat_cardinalities"],
            num_classes=arch["num_classes"],
            embedding_dim=arch["embedding_dim"],
            num_heads=arch["num_heads"],
            num_layers=arch["num_layers"],
            feedforward_dim=arch.get("feedforward_dim", 128),
            dropout=arch.get("dropout", 0.1)
        )
        self.model.load_state_dict(torch.load(weights_path, map_location=torch.device("cpu")))
        self.model.eval()
        self.active_model_name = model_name
def _safe_float(val: Any, default: float = 0.0) -> float:
    if val is None or val == "":
        return default
    try:
        f = float(val)
        return default if np.isnan(f) else f
    except (ValueError, TypeError):
        return default


def extract_and_validate_features(flow_dict: Dict[str, Any]) -> Tuple[Dict[str, float], Dict[str, str]]:
    """Intelligently extracts, validates, and computes the 20 standard numerical features
    and 2 categorical features required by FlowTransformer from raw flow inputs.
    """
    # 1. Flow Duration
    dur_raw = (
        flow_dict.get("flow_duration")
        or flow_dict.get("Flow Duration")
        or flow_dict.get("flow_duration_milliseconds")
        or flow_dict.get("FLOW_DURATION_MILLISECONDS")
        or flow_dict.get("duration")
    )
    flow_duration = max(_safe_float(dur_raw, default=100.0), 0.001)

    # 2. Packet counts
    fwd_pkts = _safe_float(
        flow_dict.get("fwd_pkts") or flow_dict.get("Total Fwd Packets") or flow_dict.get("in_pkts") or flow_dict.get("IN_PKTS"),
        default=1.0
    )
    bwd_pkts = _safe_float(
        flow_dict.get("bwd_pkts") or flow_dict.get("Total Backward Packets") or flow_dict.get("out_pkts") or flow_dict.get("OUT_PKTS"),
        default=0.0
    )

    # 3. Byte counts
    fwd_bytes = _safe_float(
        flow_dict.get("fwd_bytes") or flow_dict.get("Total Length of Fwd Packets") or flow_dict.get("in_bytes") or flow_dict.get("IN_BYTES"),
        default=64.0
    )
    bwd_bytes = _safe_float(
        flow_dict.get("bwd_bytes") or flow_dict.get("Total Length of Bwd Packets") or flow_dict.get("out_bytes") or flow_dict.get("OUT_BYTES"),
        default=0.0
    )

    # 4. Rates
    dur_sec = max(flow_duration / 1000.0 if flow_duration > 50 else flow_duration, 1e-4)
    flow_rate_bytes_per_sec = _safe_float(
        flow_dict.get("flow_rate_bytes_per_sec") or flow_dict.get("flow_rate"),
        default=(fwd_bytes + bwd_bytes) / dur_sec
    )
    flow_rate_pkts_per_sec = _safe_float(
        flow_dict.get("flow_rate_pkts_per_sec") or flow_dict.get("packet_rate"),
        default=(fwd_pkts + bwd_pkts) / dur_sec
    )

    # 5. Packet lengths
    tot_pkts = max(fwd_pkts + bwd_pkts, 1.0)
    tot_bytes = fwd_bytes + bwd_bytes
    pkt_len_mean = _safe_float(flow_dict.get("pkt_len_mean"), default=tot_bytes / tot_pkts)
    pkt_len_std = _safe_float(flow_dict.get("pkt_len_std"), default=abs(fwd_bytes - bwd_bytes) / tot_pkts)
    pkt_len_max = _safe_float(flow_dict.get("pkt_len_max") or flow_dict.get("longest_flow_pkt"), default=max(fwd_bytes, bwd_bytes))
    pkt_len_min = _safe_float(flow_dict.get("pkt_len_min") or flow_dict.get("shortest_flow_pkt"), default=min(fwd_bytes, bwd_bytes) / tot_pkts)
    fwd_pkt_len_mean = _safe_float(flow_dict.get("fwd_pkt_len_mean"), default=fwd_bytes / max(fwd_pkts, 1.0))
    bwd_pkt_len_mean = _safe_float(flow_dict.get("bwd_pkt_len_mean"), default=bwd_bytes / max(bwd_pkts, 1.0))

    # 6. Inter-Arrival Times (IAT)
    iat_mean = _safe_float(flow_dict.get("iat_mean") or flow_dict.get("src_to_dst_iat_avg"), default=flow_duration / tot_pkts)
    iat_std = _safe_float(flow_dict.get("iat_std") or flow_dict.get("src_to_dst_iat_stddev"), default=iat_mean * 0.5)
    iat_max = _safe_float(flow_dict.get("iat_max") or flow_dict.get("src_to_dst_iat_max"), default=flow_duration)

    # 7. TCP Flags
    tcp_flags_raw = flow_dict.get("tcp_flags") or flow_dict.get("TCP_FLAGS") or 0
    try:
        tflags = int(tcp_flags_raw)
    except (ValueError, TypeError):
        tflags = 0

    def _resolve_flag(key1: str, key2: str, bitmask: int) -> float:
        v1 = flow_dict.get(key1)
        if v1 is not None and v1 != "":
            return _safe_float(v1)
        v2 = flow_dict.get(key2)
        if v2 is not None and v2 != "":
            return _safe_float(v2)
        return 1.0 if (tflags & bitmask) > 0 else 0.0

    tcp_flags_syn = _resolve_flag("tcp_flags_syn", "SYN Flag Count", 2)
    tcp_flags_ack = _resolve_flag("tcp_flags_ack", "ACK Flag Count", 16)
    tcp_flags_fin = _resolve_flag("tcp_flags_fin", "FIN Flag Count", 1)
    tcp_flags_rst = _resolve_flag("tcp_flags_rst", "RST Flag Count", 4)

    numericals = {
        "flow_duration": flow_duration,
        "fwd_pkts": fwd_pkts,
        "bwd_pkts": bwd_pkts,
        "fwd_bytes": fwd_bytes,
        "bwd_bytes": bwd_bytes,
        "flow_rate_bytes_per_sec": flow_rate_bytes_per_sec,
        "flow_rate_pkts_per_sec": flow_rate_pkts_per_sec,
        "pkt_len_mean": pkt_len_mean,
        "pkt_len_std": pkt_len_std,
        "pkt_len_max": pkt_len_max,
        "pkt_len_min": pkt_len_min,
        "fwd_pkt_len_mean": fwd_pkt_len_mean,
        "bwd_pkt_len_mean": bwd_pkt_len_mean,
        "iat_mean": iat_mean,
        "iat_std": iat_std,
        "iat_max": iat_max,
        "tcp_flags_syn": tcp_flags_syn,
        "tcp_flags_ack": tcp_flags_ack,
        "tcp_flags_fin": tcp_flags_fin,
        "tcp_flags_rst": tcp_flags_rst
    }

    # Categoricals
    proto_raw = str(flow_dict.get("protocol") or flow_dict.get("Protocol") or flow_dict.get("PROTOCOL") or "6").strip().lower()
    if proto_raw in ["tcp", "6"]:
        protocol_val = "6"
    elif proto_raw in ["udp", "17"]:
        protocol_val = "17"
    elif proto_raw in ["icmp", "1"]:
        protocol_val = "1"
    elif proto_raw in ["igmp", "2"]:
        protocol_val = "2"
    else:
        protocol_val = proto_raw

    dst_port_raw = flow_dict.get("dst_port") or flow_dict.get("Destination Port") or flow_dict.get("L4_DST_PORT") or 80
    try:
        dp = int(dst_port_raw)
    except (ValueError, TypeError):
        dp = 80

    if dp in [80, 443, 8080, 8443]:
        port_cat = "web"
    elif dp == 53:
        port_cat = "dns"
    elif dp == 22:
        port_cat = "ssh"
    elif dp in [20, 21]:
        port_cat = "ftp"
    else:
        port_cat = "other"

    categoricals = {
        "protocol": protocol_val,
        "dst_port_category": port_cat
    }

    return numericals, categoricals


class ModelInferenceService:
    def __init__(self):
        self.active_model_name: Optional[str] = None
        self.model: Optional[FlowTransformer] = None
        self.preprocessor: Optional[FlowPreprocessor] = None
        self.metadata: Optional[Dict[str, Any]] = None

    def load_model(self, model_name: str) -> bool:
        model_dir = os.path.join(settings.ARTIFACTS_DIR, model_name)
        weights_path = os.path.join(model_dir, "weights.pt")
        prep_path = os.path.join(model_dir, "preprocessor.json")
        meta_path = os.path.join(model_dir, "metadata.json")

        if not (os.path.exists(weights_path) and os.path.exists(prep_path) and os.path.exists(meta_path)):
            logger.warning(f"Model artifacts not found for '{model_name}' in {model_dir}")
            return False

        with open(meta_path, "r") as f:
            self.metadata = json.load(f)

        self.preprocessor = FlowPreprocessor.load(prep_path)
        arch = self.metadata["architecture_config"]
        
        self.model = FlowTransformer(
            num_numerical=arch["num_numerical"],
            cat_cardinalities=arch["cat_cardinalities"],
            num_classes=arch["num_classes"],
            embedding_dim=arch["embedding_dim"],
            num_heads=arch["num_heads"],
            num_layers=arch["num_layers"],
            feedforward_dim=arch.get("feedforward_dim", 128),
            dropout=arch.get("dropout", 0.1)
        )
        self.model.load_state_dict(torch.load(weights_path, map_location=torch.device("cpu")))
        self.model.eval()
        self.active_model_name = model_name
        logger.info(f"Loaded FlowTransformer model '{model_name}' successfully for inference.")
        return True

    def extract_and_validate_features(self, flow_dict: Dict[str, Any]) -> Tuple[Dict[str, float], Dict[str, str]]:
        return extract_and_validate_features(flow_dict)

    def predict_flow(self, flow_dict: Dict[str, Any]) -> Dict[str, Any]:
        if self.model is None or self.preprocessor is None:
            raise RuntimeError("No active trained FlowTransformer model loaded. Please train or select an active model first.")

        start_time = time.time()
        
        # 1. Feature Extraction, Validation, and Normalization
        numericals, categoricals = extract_and_validate_features(flow_dict)
        combined_features = {**numericals, **categoricals}
        df_row = pd.DataFrame([combined_features])

        X_num, X_cat = self.preprocessor.transform(df_row)
        t_num = torch.tensor(X_num, dtype=torch.float32)
        t_cat = torch.tensor(X_cat, dtype=torch.long)

        # 2. Transformer Forward pass
        bin_probs, multi_probs = self.model.predict_proba(t_num, t_cat)
        
        bin_prob_val = float(bin_probs[0].item())
        multi_probs_arr = multi_probs[0].cpu().numpy()
        
        pred_idx = int(np.argmax(multi_probs_arr))
        raw_predicted_class = self.preprocessor.idx_to_target_class.get(pred_idx, LABEL_BENIGN)
        raw_confidence = float(multi_probs_arr[pred_idx])

        # 3. Dual-Head Open-Set Anomaly Detection & Arbitration
        # If binary head detects malicious anomaly (>=0.50), but multiclass confidence on known classes is low (<0.40)
        # or points to Benign, we flag as Unknown/Suspicious Anomaly to avoid forcing into wrong categories.
        OPEN_SET_THRESHOLD = 0.40
        is_anomaly = False

        if bin_prob_val >= 0.50:
            if raw_predicted_class == LABEL_BENIGN or raw_confidence < OPEN_SET_THRESHOLD:
                predicted_class = "Unknown / Suspicious Anomaly"
                is_anomaly = True
                is_malicious = True
                confidence = round(max(bin_prob_val, raw_confidence), 4)
            else:
                predicted_class = raw_predicted_class
                is_anomaly = False
                is_malicious = True
                confidence = round(raw_confidence, 4)
        else:
            if raw_predicted_class != LABEL_BENIGN and raw_confidence >= 0.75:
                # Multiclass has high conviction on specific attack pattern
                predicted_class = raw_predicted_class
                is_anomaly = False
                is_malicious = True
                confidence = round(raw_confidence, 4)
            else:
                predicted_class = LABEL_BENIGN
                is_anomaly = False
                is_malicious = False
                confidence = round(max(float(multi_probs_arr[0]), 1.0 - bin_prob_val), 4)

        # Probabilities dictionary
        prob_dict = {
            self.preprocessor.idx_to_target_class[i]: round(float(multi_probs_arr[i]), 4)
            for i in range(len(multi_probs_arr))
        }

        # Explainability attributions
        top_features = compute_feature_contributions(
            model=self.model,
            x_num=t_num,
            x_cat=t_cat,
            feature_names=self.preprocessor.numerical_features,
            predicted_class_idx=pred_idx,
            raw_feature_values=combined_features
        )

        metadata_dict = {
            "src_ip": flow_dict.get("src_ip") or flow_dict.get("IPV4_SRC_ADDR") or "192.168.1.100",
            "dst_ip": flow_dict.get("dst_ip") or flow_dict.get("IPV4_DST_ADDR") or "10.0.0.5",
            "dst_port": flow_dict.get("dst_port") or flow_dict.get("L4_DST_PORT") or 80,
        }

        if is_anomaly:
            human_explanation = (
                f"FlowTransformer detected anomalous traffic from {metadata_dict['src_ip']} to "
                f"{metadata_dict['dst_ip']}:{metadata_dict['dst_port']} with an anomaly probability of {confidence*100:.1f}%. "
                f"Feature patterns diverge from known attack baselines, indicating unfamiliar behavior or an unclassified exploit vector."
            )
        else:
            human_explanation = generate_human_readable_explanation(
                predicted_class=predicted_class,
                confidence=confidence,
                is_malicious=is_malicious,
                top_features=top_features,
                metadata=metadata_dict
            )

        llm_interp = llm_provider.enrich_explanation(
            predicted_class=predicted_class,
            confidence=confidence,
            evidence=combined_features,
            top_features=top_features
        )

        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "is_malicious": is_malicious,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "binary_score": round(bin_prob_val, 4),
            "is_anomaly": is_anomaly,
            "class_probabilities": prob_dict,
            "inference_time_ms": latency_ms,
            "model_version": self.active_model_name,
            "feature_importances": top_features,
            "human_explanation": human_explanation,
            "model_evidence": {k: combined_features.get(k) for k in list(combined_features.keys())[:12]},
            "llm_interpretation": llm_interp
        }

inference_service = ModelInferenceService()

