"""STIX 2.1 Threat Intelligence Export Module.

Converts internal IOCs, alerts, flows, and MITRE mappings into
standardized STIX 2.1 JSON Bundles for sharing and ingestion by TAXII servers.
"""

import uuid
import datetime
from typing import List, Dict, Any
from app.models.cti import IOC
from app.models.alert import Alert


def export_iocs_to_stix(iocs: List[IOC], alerts: List[Alert]) -> Dict[str, Any]:
    """Serializes IOCs and related Alerts into a STIX 2.1 Bundle."""
    bundle_id = f"bundle--{uuid.uuid4()}"
    objects = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Identity object (The NIDS Platform)
    identity_id = f"identity--{uuid.uuid4()}"
    objects.append({
        "type": "identity",
        "spec_version": "2.1",
        "id": identity_id,
        "created": now_iso,
        "modified": now_iso,
        "name": "Transformer-Based NIDS & CTI Platform",
        "identity_class": "system",
        "description": "Autonomous AI-powered network intrusion detection and threat intelligence platform"
    })

    # 2. Indicators
    for ioc in iocs:
        ind_id = f"indicator--{uuid.uuid4()}"
        
        # STIX 2.1 pattern syntax
        pattern = f"[ipv4-addr:value = '{ioc.value}']"
        if ioc.ioc_type == "sha256":
            pattern = f"[file:hashes.'SHA-256' = '{ioc.value}']"
        elif ioc.ioc_type == "domain":
            pattern = f"[domain-name:value = '{ioc.value}']"
        elif ioc.ioc_type == "port":
            pattern = f"[network-traffic:dst_port = {ioc.value.replace('port:', '')}]"

        indicator_types = ioc.threat_types if ioc.threat_types else ["malicious-activity"]

        objects.append({
            "type": "indicator",
            "spec_version": "2.1",
            "id": ind_id,
            "created": ioc.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if ioc.created_at else now_iso,
            "modified": now_iso,
            "name": f"Observed IOC {ioc.value}",
            "description": ioc.description or f"Network indicator observed with status {ioc.verification_status}",
            "indicator_types": indicator_types,
            "pattern": pattern,
            "pattern_type": "stix",
            "valid_from": now_iso,
            "confidence": int(ioc.confidence_score * 100),
            "created_by_ref": identity_id,
            "custom_properties": {
                "x_observed_status": ioc.observed_status,
                "x_verification_status": ioc.verification_status,
                "x_reputation_score": ioc.reputation_score
            }
        })

    # 3. Alerts as observed-data / incident objects
    for a in alerts:
        obs_id = f"observed-data--{uuid.uuid4()}"
        objects.append({
            "type": "observed-data",
            "spec_version": "2.1",
            "id": obs_id,
            "created": a.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if a.created_at else now_iso,
            "modified": now_iso,
            "first_observed": a.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if a.created_at else now_iso,
            "last_observed": now_iso,
            "number_observed": 1,
            "created_by_ref": identity_id,
            "custom_properties": {
                "x_alert_code": a.alert_code,
                "x_category": a.category,
                "x_severity": a.severity,
                "x_risk_score": a.risk_score,
                "x_mitre_technique": a.mitre_technique_id
            }
        })

    return {
        "type": "bundle",
        "id": bundle_id,
        "spec_version": "2.1",
        "objects": objects
    }
