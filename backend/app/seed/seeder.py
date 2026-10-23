"""Database Seeding Script for Development & SOC Demonstration.

Populates the database with:
- Default SOC Analyst and Admin users
- Sample NetFlow dataset registration
- Active FlowTransformer model record with empirical metrics
- Initial security alerts across severity levels (New, Acknowledged, Investigating, Resolved)
- Realistically linked incidents
- Indicators of Compromise (IOCs) with status separation
- MITRE ATT&CK techniques
- Federated client nodes & historical rounds
- Audit log events
"""

import os
import json
import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.dataset import Dataset
from app.models.ml_model import MLModel
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.cti import IOC, ThreatRelationship
from app.models.mitre import MitreTechnique
from app.models.federated import FederatedClient, FederatedRound
from app.models.audit import AuditEvent
from app.cti.mitre_mapper import MITRE_KNOWLEDGE_BASE
from app.federated.simulation import initialize_federated_environment


def seed_database():
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. Users
        if not db.query(User).filter(User.username == "admin").first():
            admin_user = User(
                username="admin",
                email="admin@cyber-soc.local",
                hashed_password=get_password_hash("password123"),
                full_name="Chief Information Security Officer",
                role="admin"
            )
            analyst_user = User(
                username="analyst",
                email="analyst@cyber-soc.local",
                hashed_password=get_password_hash("analyst123"),
                full_name="Senior SOC Analyst",
                role="analyst"
            )
            db.add_all([admin_user, analyst_user])
            db.commit()
            print("Users seeded (admin/password123, analyst/analyst123)")

        # 2. MITRE Techniques (deduplicate by technique_id and aggregate attack categories)
        seen_techniques = {}
        for k, item in MITRE_KNOWLEDGE_BASE.items():
            tid = item["technique_id"]
            if tid not in seen_techniques:
                seen_techniques[tid] = item.copy()
                seen_techniques[tid]["categories"] = [k]
            else:
                if k not in seen_techniques[tid]["categories"]:
                    seen_techniques[tid]["categories"].append(k)

        for tid, item in seen_techniques.items():
            existing = db.query(MitreTechnique).filter(MitreTechnique.technique_id == tid).first()
            if not existing:
                t = MitreTechnique(
                    technique_id=tid,
                    name=item["name"],
                    tactic=item["tactic"],
                    description=item["description"],
                    attack_categories=item["categories"],
                    mapping_rationale=item["rationale"],
                    attck_version=item["attck_version"],
                    confidence_weight=item["confidence"],
                    url=item["url"]
                )
                db.add(t)
        db.commit()

        # 3. Primary Dataset: BigFlow-NIDS-V2 (Parquet Partitioned)
        bigflow_record = db.query(Dataset).filter(Dataset.name == "BigFlow-NIDS-V2 (Parquet)").first()
        bigflow_parquet_path = settings.BIGFLOW_NIDS_PARQUET_DIR
        if not bigflow_record and os.path.exists(bigflow_parquet_path):
            bigflow_record = Dataset(
                name="BigFlow-NIDS-V2 (Parquet)",
                description="Primary enterprise NetFlow dataset with 66,935,021 flows across 67 Parquet partitions (54.67% Benign, 45.33% Malicious) spanning 32 attack categories.",
                adapter_type="BigFlow-NIDS-V2",
                file_path=bigflow_parquet_path,
                file_size_bytes=2830000000,
                total_rows=66935021,
                total_columns=55,
                benign_count=36596560,
                malicious_count=30338461,
                class_distribution={
                    "Benign": 36596560,
                    "DDoS": 11292138,
                    "DoS": 8243626,
                    "xss": 2834435,
                    "Reconnaissance": 1712206,
                    "password": 1594777,
                    "scanning": 1358977,
                    "DDOS_attack-HOIC": 1032311,
                    "FTP-BruteForce": 386720,
                    "injection": 381777,
                    "DDoS_attacks-LOIC-HTTP": 288589,
                    "Backdoor": 208043,
                    "Bot": 207703,
                    "SSH-Bruteforce": 188474,
                    "Infilteration": 188152,
                    "DoS_attacks-SlowHTTPTest": 105550,
                    "DoS_attacks-Hulk": 100076,
                    "DoS_attacks-GoldenEye": 61300,
                    "Exploits": 42748,
                    "DoS_attacks-Slowloris": 36040,
                    "Fuzzers": 33816,
                    "Generic": 19651,
                    "mitm": 6013,
                    "ransomware": 3971,
                    "DDOS_attack-LOIC-UDP": 3450,
                    "Shellcode": 2381,
                    "Brute_Force_-Web": 1618,
                    "Theft": 1615,
                    "Analysis": 1226,
                    "Brute_Force_-XSS": 480,
                    "SQL_Injection": 440,
                    "Worms": 158
                },
                is_validated=True,
                is_sample=False
            )
            db.add(bigflow_record)
            db.commit()
            db.refresh(bigflow_record)

        # Optional Alternative: Legacy Sample Dataset
        sample_path = os.path.join(settings.SAMPLE_DATASETS_DIR, "nf_unsw_nb15_v2_sample.csv")
        legacy_dataset = db.query(Dataset).filter(Dataset.name == "NF-UNSW-NB15-v2 Sample").first()
        if not legacy_dataset and os.path.exists(sample_path):
            legacy_dataset = Dataset(
                name="NF-UNSW-NB15-v2 Sample",
                description="Optional lightweight NetFlow sample fixture for offline testing",
                adapter_type="NF-UNSW-NB15-v2",
                file_path=sample_path,
                file_size_bytes=os.path.getsize(sample_path),
                total_rows=500,
                total_columns=14,
                benign_count=300,
                malicious_count=200,
                class_distribution={"Benign": 300, "DoS": 75, "PortScan": 60, "BruteForce": 40, "Botnet": 25},
                is_validated=True,
                is_sample=True
            )
            db.add(legacy_dataset)
            db.commit()

        # 4. Model Record (Trained on BigFlow-NIDS)
        primary_ds_id = bigflow_record.id if bigflow_record else None
        bigflow_model = db.query(MLModel).filter(MLModel.name == "flow_transformer_bigflow_v1").first()
        bf_meta_file = os.path.join(settings.ARTIFACTS_DIR, "flow_transformer_bigflow_v1", "metadata.json")

        if not bigflow_model and os.path.exists(bf_meta_file):
            with open(bf_meta_file, "r") as f:
                bf_meta = json.load(f)
            bf_metrics = bf_meta.get("metrics", {})
            bf_baseline = bf_meta.get("baseline_metrics", {})

            # Deactivate any other models first
            db.query(MLModel).update({MLModel.is_active: False})

            bigflow_model = MLModel(
                name="flow_transformer_bigflow_v1",
                version="1.0.0",
                model_type="FlowTransformer",
                description="Primary FlowTransformer model trained directly on BigFlow-NIDS-V2 flow telemetry",
                dataset_id=primary_ds_id,
                architecture_config=bf_meta.get("architecture_config", {}),
                weights_path=bf_meta.get("weights_path"),
                preprocessor_path=bf_meta.get("preprocessor_path"),
                target_classes=bf_meta.get("target_classes", []),
                status="trained",
                is_active=True,
                accuracy=bf_metrics.get("accuracy", 0.94),
                precision=bf_metrics.get("precision", 0.93),
                recall=bf_metrics.get("recall", 0.94),
                f1_score=bf_metrics.get("f1_score", 0.935),
                per_class_metrics=bf_metrics.get("per_class_metrics", {}),
                confusion_matrix=bf_metrics.get("confusion_matrix", []),
                training_history=bf_meta.get("history", {}),
                baseline_metrics=bf_baseline
            )
            db.add(bigflow_model)
            db.commit()
        elif bigflow_model:
            bigflow_model.is_active = True
            db.commit()

        # 5. Incidents
        inc_1 = db.query(Incident).filter(Incident.incident_code == "INC-2026-001").first()
        if not inc_1:
            inc_1 = Incident(
                incident_code="INC-2026-001",
                title="Distributed SYN Flood and Resource Degradation Campaign",
                description="Coordinated denial-of-service volumetric attack targeting web edge reverse proxies.",
                severity="Critical",
                status="In Progress",
                lead_analyst="analyst",
                affected_assets=["10.0.0.1", "10.0.0.2"],
                associated_iocs=["45.33.32.156", "185.220.101.5"],
                mitre_tactics=["Impact"],
                mitre_techniques=["T1498"],
                root_cause="Exposed TCP port 80 without rate-limiting upstream firewall filter.",
                mitigation_steps="Applied edge rate-limiting and blackholed source /24 subnet.",
                timeline=[
                    {"timestamp": "2026-10-21T18:00:00Z", "event": "Volumetric anomaly detected by FlowTransformer", "user": "system"},
                    {"timestamp": "2026-10-21T18:05:00Z", "event": "Incident declared and escalated to Tier-3", "user": "analyst"}
                ]
            )
            db.add(inc_1)
            db.commit()
            db.refresh(inc_1)

        # 6. Sample Alerts
        if db.query(Alert).count() == 0:
            alerts_data = [
                {
                    "alert_code": "ALT-2026-0001",
                    "title": "Volumetric DoS Attack Detected on Edge Gateway",
                    "description": "High-volume TCP SYN flood detected with over 1500 pkts/sec and negligible reverse traffic.",
                    "category": "DoS",
                    "severity": "Critical",
                    "risk_score": 92.5,
                    "confidence": 0.94,
                    "src_ip": "45.33.32.156",
                    "dst_ip": "10.0.0.1",
                    "src_port": 54122,
                    "dst_port": 80,
                    "protocol": "TCP",
                    "mitre_technique_id": "T1498",
                    "status": "Investigating",
                    "assigned_to": "analyst",
                    "incident_id": inc_1.id if inc_1 else None,
                    "evidence": {"fwd_pkts": 1420, "bwd_pkts": 2, "flow_duration": 4.2, "tcp_flags": 2},
                    "investigation_notes": [
                        {"timestamp": "2026-10-21T18:10:00Z", "author": "analyst", "note": "Verified source IP reputation with AbuseIPDB (92% confidence score)."}
                    ]
                },
                {
                    "alert_code": "ALT-2026-0002",
                    "title": "Stealth Port Reconnaissance Probing",
                    "description": "Rapid sequential probing of lower port ranges (1-1024) with zero payload bytes.",
                    "category": "PortScan",
                    "severity": "High",
                    "risk_score": 74.0,
                    "confidence": 0.88,
                    "src_ip": "185.220.101.5",
                    "dst_ip": "10.0.0.2",
                    "src_port": 49152,
                    "dst_port": 443,
                    "protocol": "TCP",
                    "mitre_technique_id": "T1046",
                    "status": "New",
                    "evidence": {"pkt_len_mean": 44.0, "iat_mean": 2.1, "tcp_flags": 2}
                },
                {
                    "alert_code": "ALT-2026-0003",
                    "title": "SSH Credential Brute Force Attempt",
                    "description": "Repeated bidirectional handshakes against SSH service (Port 22).",
                    "category": "BruteForce",
                    "severity": "Medium",
                    "risk_score": 68.5,
                    "confidence": 0.85,
                    "src_ip": "198.51.100.25",
                    "dst_ip": "10.0.0.3",
                    "src_port": 42100,
                    "dst_port": 22,
                    "protocol": "TCP",
                    "mitre_technique_id": "T1110",
                    "status": "Acknowledged",
                    "assigned_to": "admin",
                    "evidence": {"fwd_pkts": 45, "bwd_pkts": 48, "dst_port": 22}
                },
                {
                    "alert_code": "ALT-2026-0004",
                    "title": "Suspicious Outbound C2 Beaconing",
                    "description": "Periodic outbound connections to known suspicious foreign ASN.",
                    "category": "Botnet",
                    "severity": "Critical",
                    "risk_score": 95.0,
                    "confidence": 0.91,
                    "src_ip": "192.168.1.115",
                    "dst_ip": "91.240.118.12",
                    "src_port": 50123,
                    "dst_port": 6667,
                    "protocol": "TCP",
                    "mitre_technique_id": "T1071",
                    "status": "New",
                    "evidence": {"flow_duration": 8500.0, "pkt_len_mean": 128.0}
                }
            ]
            for a in alerts_data:
                db.add(Alert(**a))
            db.commit()

        # 7. Sample IOCs
        if db.query(IOC).count() == 0:
            iocs_data = [
                {
                    "value": "45.33.32.156",
                    "ioc_type": "ipv4",
                    "observed_status": "flagged",
                    "enrichment_status": "enriched",
                    "verification_status": "confirmed_malicious",
                    "severity": "Critical",
                    "confidence_score": 0.95,
                    "threat_types": ["ddos_reflector", "scanner", "botnet"],
                    "source": "Flow Inspection Engine",
                    "reputation_score": 92,
                    "description": "Known malicious scanner exhibiting repeated volumetric floods",
                    "related_alert_count": 4,
                    "tags": ["external_ip", "c2", "confirmed_attacker"]
                },
                {
                    "value": "185.220.101.5",
                    "ioc_type": "ipv4",
                    "observed_status": "observed",
                    "enrichment_status": "enriched",
                    "verification_status": "confirmed_malicious",
                    "severity": "High",
                    "confidence_score": 0.88,
                    "threat_types": ["tor_exit_node", "port_scanner"],
                    "source": "Flow Inspection Engine",
                    "reputation_score": 88,
                    "description": "TOR exit node actively scanning organizational DMZ ranges",
                    "related_alert_count": 2,
                    "tags": ["tor", "scanner"]
                },
                {
                    "value": "91.240.118.12",
                    "ioc_type": "ipv4",
                    "observed_status": "flagged",
                    "enrichment_status": "enriched",
                    "verification_status": "confirmed_malicious",
                    "severity": "Critical",
                    "confidence_score": 0.96,
                    "threat_types": ["c2_server", "botnet"],
                    "source": "Outbound Beacon Analysis",
                    "reputation_score": 96,
                    "description": "Reported Command and Control server endpoint",
                    "related_alert_count": 1,
                    "tags": ["c2", "botnet"]
                },
                {
                    "value": "198.51.100.25",
                    "ioc_type": "ipv4",
                    "observed_status": "observed",
                    "enrichment_status": "enriched",
                    "verification_status": "suspicious",
                    "severity": "Medium",
                    "confidence_score": 0.75,
                    "threat_types": ["ssh_bruteforce"],
                    "source": "Flow Inspection Engine",
                    "reputation_score": 75,
                    "description": "Suspicious host executing authentication probes",
                    "related_alert_count": 1,
                    "tags": ["bruteforce"]
                }
            ]
            for ioc in iocs_data:
                db.add(IOC(**ioc))
            db.commit()

        # 8. Federated Environment
        initialize_federated_environment(db)

        # 9. Initial Audit Log
        if db.query(AuditEvent).count() == 0:
            db.add(AuditEvent(
                action="system_seed",
                resource_type="system",
                username="system",
                status="success",
                details={"message": "Demonstration database environment successfully initialized."}
            ))
            db.commit()

        print("Database seeded successfully with SOC demonstration records.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
