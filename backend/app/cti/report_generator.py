"""Report Generation Subsystem.

Generates comprehensive executive incident reports, model performance audits,
and CTI summaries in Markdown, JSON, and CSV.
"""

import os
import json
import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.ml_model import MLModel
from app.models.cti import IOC


def generate_executive_soc_report(db: Session) -> str:
    """Generates an Executive SOC Summary Report in Markdown."""
    now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    total_alerts = db.query(Alert).count()
    critical_alerts = db.query(Alert).filter(Alert.severity == "Critical").count()
    open_incidents = db.query(Incident).filter(Incident.status.in_(["Open", "In Progress"])).count()
    total_iocs = db.query(IOC).count()
    confirmed_malicious_iocs = db.query(IOC).filter(IOC.verification_status == "confirmed_malicious").count()
    active_model = db.query(MLModel).filter(MLModel.is_active == True).first()

    report_lines = [
        "# EXECUTIVE CYBERSECURITY & THREAT INTELLIGENCE REPORT",
        f"**Generated:** {now_str}  ",
        "**Classification:** RESTRICTED // SOC OPERATIONAL INTELLIGENCE  ",
        "**System:** Autonomous FlowTransformer NIDS Platform  ",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        f"During the current monitoring window, the platform observed **{total_alerts} security alerts**, "
        f"including **{critical_alerts} critical severity events** requiring Tier-3 analyst investigation. "
        f"A total of **{open_incidents} high-impact security incidents** are actively undergoing containment.",
        "",
        "## 2. Key Threat Metrics",
        f"| Metric | Current Count | Status / Severity |",
        f"| :--- | :--- | :--- |",
        f"| Total Alerts | {total_alerts} | Monitored |",
        f"| Critical Risk Detections | {critical_alerts} | Escalated |",
        f"| Active Incidents | {open_incidents} | In Progress |",
        f"| Indicators of Compromise (IOCs) | {total_iocs} | Verified Malicious: {confirmed_malicious_iocs} |",
        "",
        "## 3. Active AI Model Status",
    ]

    if active_model:
        report_lines.extend([
            f"- **Model Architecture:** {active_model.model_type}",
            f"- **Version Tag:** `{active_model.version}`",
            f"- **Held-Out Test Accuracy:** `{active_model.accuracy * 100:.2f}%`" if active_model.accuracy else "- Held-out Accuracy: Pending",
            f"- **Macro F1-Score:** `{active_model.f1_score:.4f}`" if active_model.f1_score else "- F1-Score: Pending",
            f"- **Supported Target Classes:** {', '.join(active_model.target_classes or [])}"
        ])
    else:
        report_lines.append("- *No model currently marked active.*")

    report_lines.extend([
        "",
        "## 4. Recommendations & Incident Response Actions",
        "1. **Enforce Firewall Egress Filters:** Block outbound communication to verified malicious C2 IOCs.",
        "2. **Patch Identified Attack Vectors:** Audit internet-facing assets targeted by repeated reconnaissance (T1046) and brute force attempts (T1110).",
        "3. **Synchronize Federated Defense:** Participate in scheduled collaborative rounds to adapt detection weights to emerging cross-sector threat vectors.",
        "",
        "---",
        "*Report autonomously synthesized by Transformer-Based NIDS & Cyber Threat Intelligence Platform.*"
    ])

    report_content = "\n".join(report_lines)
    
    # Save copy to reports directory
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    report_filename = f"soc_report_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
    file_path = os.path.join(settings.REPORTS_DIR, report_filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_content
