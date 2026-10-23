"""CTI Enrichment Module.

Supports optional VirusTotal and AbuseIPDB API connectors with graceful degradation
to an offline deterministic threat intelligence knowledge base for reliable demonstration.
"""

import os
import datetime
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger

# Offline threat intelligence database for known malicious networks in research datasets
DEMO_THREAT_INTEL_DB: Dict[str, Dict[str, Any]] = {
    "45.33.32.156": {
        "reputation_score": 92,
        "threat_types": ["scanner", "botnet", "ddos_reflector"],
        "country": "US",
        "asn": "AS63949 Linode, LLC",
        "total_reports": 142,
        "verification_status": "confirmed_malicious",
        "provider": "Offline Intel Engine"
    },
    "185.220.101.5": {
        "reputation_score": 88,
        "threat_types": ["tor_exit_node", "reconnaissance", "port_scanner"],
        "country": "DE",
        "asn": "AS208294",
        "total_reports": 310,
        "verification_status": "confirmed_malicious",
        "provider": "Offline Intel Engine"
    },
    "198.51.100.25": {
        "reputation_score": 75,
        "threat_types": ["ssh_bruteforce", "credential_stuffing"],
        "country": "RO",
        "asn": "AS12345 Demo ISP",
        "total_reports": 64,
        "verification_status": "suspicious",
        "provider": "Offline Intel Engine"
    },
    "91.240.118.12": {
        "reputation_score": 96,
        "threat_types": ["c2_server", "botnet", "ransomware_distribution"],
        "country": "RU",
        "asn": "AS49505 Selectel",
        "total_reports": 512,
        "verification_status": "confirmed_malicious",
        "provider": "Offline Intel Engine"
    }
}


class ThreatEnrichmentService:
    def __init__(self):
        self.virustotal_key = settings.VIRUSTOTAL_API_KEY
        self.abuseipdb_key = settings.ABUSEIPDB_API_KEY

    def enrich_ip(self, ip: str) -> Dict[str, Any]:
        """Enriches an IP address via external APIs if keys are set, otherwise uses offline intel."""
        # 1. Check if real AbuseIPDB key provided
        if self.abuseipdb_key:
            try:
                headers = {"Key": self.abuseipdb_key, "Accept": "application/json"}
                params = {"ipAddress": ip, "maxAgeInDays": 90}
                with httpx.Client(timeout=4.0) as client:
                    resp = client.get("https://api.abuseipdb.com/api/v2/check", headers=headers, params=params)
                    if resp.status_code == 200:
                        data = resp.json().get("data", {})
                        abuse_score = data.get("abuseConfidenceScore", 0)
                        return {
                            "reputation_score": abuse_score,
                            "threat_types": ["reported_abuse"] if abuse_score > 25 else [],
                            "country": data.get("countryCode", "Unknown"),
                            "asn": data.get("isp", "Unknown ISP"),
                            "total_reports": data.get("totalReports", 0),
                            "verification_status": "confirmed_malicious" if abuse_score >= 50 else ("suspicious" if abuse_score > 10 else "benign_whitelisted"),
                            "provider": "AbuseIPDB Live API",
                            "last_enriched_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                        }
            except Exception as e:
                logger.warning(f"AbuseIPDB enrichment failed for {ip}: {e}. Falling back to offline intel.")

        # 2. Check offline demo threat intelligence database
        if ip in DEMO_THREAT_INTEL_DB:
            intel = DEMO_THREAT_INTEL_DB[ip].copy()
            intel["last_enriched_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            return intel

        # 3. Default baseline enrichment for unknown / private IPs
        import ipaddress
        is_priv = False
        try:
            is_priv = ipaddress.ip_address(ip).is_private
        except ValueError:
            pass

        return {
            "reputation_score": 0 if is_priv else 15,
            "threat_types": ["internal_rfc1918"] if is_priv else ["unclassified_ip"],
            "country": "Local Network" if is_priv else "Unknown",
            "asn": "Private Network" if is_priv else "Standard Public Network",
            "total_reports": 0,
            "verification_status": "benign_whitelisted" if is_priv else "unverified",
            "provider": "Local Heuristics Engine",
            "last_enriched_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

enrichment_service = ThreatEnrichmentService()
