"""Threat Correlation Engine and Graph Builder.

Relates security events, flows, and indicators by shared IP infrastructure,
targeted destination ports, common attack patterns, and MITRE techniques.
Builds node-link relationship graphs for SOC analysts.
"""

from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.cti import IOC, ThreatRelationship
from app.models.incident import Incident
from app.models.mitre import MitreTechnique


class ThreatCorrelationEngine:
    def correlate_alerts(self, db: Session) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Scans alerts and generates graph nodes & edges.
        Returns: (nodes, edges)
        """
        alerts = db.query(Alert).all()
        iocs = db.query(IOC).all()
        incidents = db.query(Incident).all()
        mitre_techs = db.query(MitreTechnique).all()

        nodes = []
        edges = []
        node_ids = set()

        # 1. Add Alert nodes
        for a in alerts:
            nid = f"alert:{a.id}"
            if nid not in node_ids:
                nodes.append({
                    "id": nid,
                    "label": f"{a.alert_code}: {a.category}",
                    "type": "alert",
                    "severity": a.severity,
                    "details": {
                        "category": a.category,
                        "risk_score": a.risk_score,
                        "src_ip": a.src_ip,
                        "dst_ip": a.dst_ip,
                        "status": a.status
                    }
                })
                node_ids.add(nid)

            # Link Alert to Source IP (IOC)
            if a.src_ip:
                ip_nid = f"ioc:{a.src_ip}"
                if ip_nid not in node_ids:
                    nodes.append({
                        "id": ip_nid,
                        "label": a.src_ip,
                        "type": "ioc",
                        "severity": a.severity,
                        "details": {"ioc_type": "ipv4", "value": a.src_ip}
                    })
                    node_ids.add(ip_nid)
                
                edges.append({
                    "id": f"e_src_{a.id}_{a.src_ip}",
                    "source": ip_nid,
                    "target": nid,
                    "relationship": "originated_from",
                    "confidence": 0.95
                })

            # Link Alert to MITRE Technique
            if a.mitre_technique_id:
                m_nid = f"mitre:{a.mitre_technique_id}"
                if m_nid not in node_ids:
                    nodes.append({
                        "id": m_nid,
                        "label": a.mitre_technique_id,
                        "type": "mitre",
                        "severity": "Informational",
                        "details": {"technique_id": a.mitre_technique_id}
                    })
                    node_ids.add(m_nid)

                edges.append({
                    "id": f"e_mitre_{a.id}_{a.mitre_technique_id}",
                    "source": nid,
                    "target": m_nid,
                    "relationship": "maps_to_technique",
                    "confidence": 0.85
                })

            # Link Alert to Incident if assigned
            if a.incident_id:
                inc_nid = f"incident:{a.incident_id}"
                if inc_nid not in node_ids:
                    nodes.append({
                        "id": inc_nid,
                        "label": f"Incident #{a.incident_id}",
                        "type": "incident",
                        "severity": "High",
                        "details": {"incident_id": a.incident_id}
                    })
                    node_ids.add(inc_nid)

                edges.append({
                    "id": f"e_inc_{a.id}_{a.incident_id}",
                    "source": nid,
                    "target": inc_nid,
                    "relationship": "part_of_incident",
                    "confidence": 1.0
                })

        # 2. Add standalone high-severity IOCs if not already included
        for ioc in iocs:
            ioc_nid = f"ioc:{ioc.value}"
            if ioc_nid not in node_ids and ioc.verification_status == "confirmed_malicious":
                nodes.append({
                    "id": ioc_nid,
                    "label": ioc.value,
                    "type": "ioc",
                    "severity": ioc.severity,
                    "details": {
                        "ioc_type": ioc.ioc_type,
                        "value": ioc.value,
                        "reputation_score": ioc.reputation_score
                    }
                })
                node_ids.add(ioc_nid)

        return nodes, edges

correlation_engine = ThreatCorrelationEngine()
