"""Sample Dataset Generator.

Generates realistic NetFlow samples reflecting benign traffic and representative attack vectors:
- DoS (SYN Flood, UDP Flood)
- PortScan (Reconnaissance, Stealth SYN scanning)
- BruteForce (SSH/FTP credential guessing)
- Botnet (C2 beacons, heartbeats)
- Benign (Web browsing, HTTPS, DNS, NTP)
"""

import os
import random
import numpy as np
import pandas as pd
from app.core.config import settings

def generate_sample_datasets():
    os.makedirs(settings.SAMPLE_DATASETS_DIR, exist_ok=True)
    np.random.seed(42)
    random.seed(42)

    # 1. NF-UNSW-NB15-v2 sample (500 rows)
    rows = []
    classes = ["Benign", "DoS", "PortScan", "BruteForce", "Botnet"]
    weights = [0.60, 0.15, 0.12, 0.08, 0.05]

    for i in range(500):
        cls = random.choices(classes, weights=weights)[0]
        is_attack = 0 if cls == "Benign" else 1

        if cls == "Benign":
            src_ip = f"192.168.1.{random.randint(10, 50)}"
            dst_ip = f"10.0.0.{random.randint(1, 5)}"
            src_port = random.randint(30000, 65000)
            dst_port = random.choice([80, 443, 53, 8080])
            protocol = 6 if dst_port != 53 else 17
            duration = random.uniform(50.0, 5000.0)
            in_pkts = random.randint(5, 50)
            out_pkts = random.randint(5, 80)
            in_bytes = in_pkts * random.randint(64, 1400)
            out_bytes = out_pkts * random.randint(64, 1400)
            tcp_flags = 24  # ACK + PSH

        elif cls == "DoS":
            src_ip = f"45.33.32.{random.randint(100, 200)}"
            dst_ip = "10.0.0.1"
            src_port = random.randint(1024, 65535)
            dst_port = 80
            protocol = 6
            duration = random.uniform(0.1, 15.0)  # Very fast bursts
            in_pkts = random.randint(100, 2000)  # High packet count
            out_pkts = random.randint(0, 5)     # Very little reply
            in_bytes = in_pkts * 60
            out_bytes = out_pkts * 40
            tcp_flags = 2  # SYN flood

        elif cls == "PortScan":
            src_ip = f"185.220.101.{random.randint(5, 30)}"
            dst_ip = "10.0.0.2"
            src_port = random.randint(40000, 60000)
            dst_port = random.randint(1, 1024)
            protocol = 6
            duration = random.uniform(1.0, 50.0)
            in_pkts = random.randint(1, 3)
            out_pkts = random.randint(0, 1)
            in_bytes = in_pkts * 44
            out_bytes = out_pkts * 40
            tcp_flags = 2  # SYN

        elif cls == "BruteForce":
            src_ip = f"198.51.100.{random.randint(10, 80)}"
            dst_ip = "10.0.0.3"
            src_port = random.randint(40000, 50000)
            dst_port = 22  # SSH
            protocol = 6
            duration = random.uniform(500.0, 2000.0)
            in_pkts = random.randint(20, 60)
            out_pkts = random.randint(20, 60)
            in_bytes = in_pkts * 200
            out_bytes = out_pkts * 200
            tcp_flags = 24

        else:  # Botnet
            src_ip = f"192.168.1.{random.randint(100, 120)}"
            dst_ip = f"91.240.118.{random.randint(1, 50)}"  # Known malicious IP pool
            src_port = random.randint(49152, 65535)
            dst_port = random.choice([6667, 8443, 4444])
            protocol = 6
            duration = random.uniform(2000.0, 10000.0)
            in_pkts = random.randint(10, 30)
            out_pkts = random.randint(10, 30)
            in_bytes = in_pkts * 128
            out_bytes = out_pkts * 128
            tcp_flags = 24

        rows.append({
            "IPV4_SRC_ADDR": src_ip,
            "L4_SRC_PORT": src_port,
            "IPV4_DST_ADDR": dst_ip,
            "L4_DST_PORT": dst_port,
            "PROTOCOL": protocol,
            "L4_SRC_PORT": src_port,
            "IN_BYTES": in_bytes,
            "OUT_BYTES": out_bytes,
            "IN_PKTS": in_pkts,
            "OUT_PKTS": out_pkts,
            "FLOW_DURATION_MILLISECONDS": duration,
            "TCP_FLAGS": tcp_flags,
            "Attack": cls,
            "Label": is_attack
        })

    df_sample = pd.DataFrame(rows)
    path = os.path.join(settings.SAMPLE_DATASETS_DIR, "nf_unsw_nb15_v2_sample.csv")
    df_sample.to_csv(path, index=False)
    print(f"Sample dataset generated at: {path} ({len(df_sample)} rows)")
    return path

if __name__ == "__main__":
    generate_sample_datasets()
