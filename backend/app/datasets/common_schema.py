"""Common NetFlow & Network Intrusion Detection Feature Schema.

Provides standardized naming, metadata mapping, and canonical attack categories
for BigFlow-NIDS-V2 (Primary) as well as legacy/research datasets
(UNSW-NB15, NF-UNSW-NB15-v2, NF-BoT-IoT-v2, Edge-IIoTset, CIC-IDS2017).
"""

from typing import List, Dict, Any

# Primary numerical feature set utilized for Transformer embeddings
STANDARD_NUMERIC_FEATURES: List[str] = [
    "flow_duration",
    "fwd_pkts",
    "bwd_pkts",
    "fwd_bytes",
    "bwd_bytes",
    "flow_rate_bytes_per_sec",
    "flow_rate_pkts_per_sec",
    "pkt_len_mean",
    "pkt_len_std",
    "pkt_len_max",
    "pkt_len_min",
    "fwd_pkt_len_mean",
    "bwd_pkt_len_mean",
    "iat_mean",
    "iat_std",
    "iat_max",
    "tcp_flags_syn",
    "tcp_flags_ack",
    "tcp_flags_fin",
    "tcp_flags_rst",
]

# Categorical features requiring integer encoding or embedding
STANDARD_CATEGORICAL_FEATURES: List[str] = [
    "protocol",
    "dst_port_category",
]

# Contextual metadata preserved for CTI, audit, and SOC display (never leaked to ML features)
CONTEXT_METADATA_FIELDS: List[str] = [
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "timestamp",
]

# Standard target labels
TARGET_LABEL_BINARY = "is_attack"
TARGET_LABEL_MULTICLASS = "attack_category"

# Default benign label
LABEL_BENIGN = "Benign"

# Canonical Attack Categories across datasets (derived from BigFlow-NIDS-V2 & NetFlow standards)
CANONICAL_ATTACK_CATEGORIES: List[str] = [
    LABEL_BENIGN,
    # High-prevalence BigFlow-NIDS categories
    "DDoS",
    "DoS",
    "xss",
    "Reconnaissance",
    "password",
    "scanning",
    "DDOS_attack-HOIC",
    "FTP-BruteForce",
    "injection",
    "DDoS_attacks-LOIC-HTTP",
    "Backdoor",
    "Bot",
    "SSH-Bruteforce",
    "Infilteration",
    "DoS_attacks-SlowHTTPTest",
    "DoS_attacks-Hulk",
    "DoS_attacks-GoldenEye",
    "Exploits",
    "DoS_attacks-Slowloris",
    "Fuzzers",
    "Generic",
    "mitm",
    "ransomware",
    "DDOS_attack-LOIC-UDP",
    "Shellcode",
    "Brute_Force_-Web",
    "Theft",
    "Analysis",
    "Brute_Force_-XSS",
    "SQL_Injection",
    "Worms",
    # Backward compatibility mappings
    "PortScan",
    "BruteForce",
    "Botnet",
    "Generic_Malicious"
]

