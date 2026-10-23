"""IOC Extractor and Normalizer.

Extracts, validates, deduplicates, and normalizes Indicators of Compromise
from raw network flows, alerts, and textual descriptions.
"""

import re
import ipaddress
from typing import List, Dict, Any, Optional

# IPv4 regex
IPV4_REGEX = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
# SHA256 regex
SHA256_REGEX = re.compile(r"\b[a-fA-F0-9]{64}\b")
# Domain regex
DOMAIN_REGEX = re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b")

# Well-known private IP ranges to distinguish external IOCs
def is_private_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_multicast
    except ValueError:
        return False


def validate_ipv4(ip_str: str) -> bool:
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except ValueError:
        return False


def extract_iocs_from_flow(flow: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extracts candidate IOCs from a flow dictionary with status separation."""
    iocs = []
    
    # 1. Source IP
    src_ip = str(flow.get("src_ip") or flow.get("IPV4_SRC_ADDR") or "").strip()
    if src_ip and validate_ipv4(src_ip):
        iocs.append({
            "value": src_ip,
            "ioc_type": "ipv4",
            "observed_status": "observed",
            "verification_status": "suspicious" if not is_private_ip(src_ip) else "unverified",
            "severity": "Medium" if not is_private_ip(src_ip) else "Low",
            "confidence_score": 0.6 if not is_private_ip(src_ip) else 0.3,
            "source": "Flow Ingestion Engine",
            "description": f"Source address in network flow traffic (Private: {is_private_ip(src_ip)})",
            "tags": ["source_ip", "flow_entity"] + (["external_ip"] if not is_private_ip(src_ip) else ["internal_ip"])
        })

    # 2. Destination IP
    dst_ip = str(flow.get("dst_ip") or flow.get("IPV4_DST_ADDR") or "").strip()
    if dst_ip and validate_ipv4(dst_ip):
        iocs.append({
            "value": dst_ip,
            "ioc_type": "ipv4",
            "observed_status": "observed",
            "verification_status": "unverified",
            "severity": "Low",
            "confidence_score": 0.4,
            "source": "Flow Ingestion Engine",
            "description": f"Destination target address in network flow (Private: {is_private_ip(dst_ip)})",
            "tags": ["destination_ip", "flow_entity"]
        })

    # 3. Suspicious Port Check
    dst_port = flow.get("dst_port") or flow.get("L4_DST_PORT")
    if dst_port:
        try:
            port_num = int(dst_port)
            # Known backdoor / trojan ports
            suspicious_ports = {
                4444: "Metasploit Default Listener",
                6667: "IRC / DarkComet Botnet C2",
                1337: "Elite Backdoor",
                31337: "Back Orifice Trojan"
            }
            if port_num in suspicious_ports:
                iocs.append({
                    "value": f"port:{port_num}",
                    "ioc_type": "port",
                    "observed_status": "flagged",
                    "verification_status": "suspicious",
                    "severity": "High",
                    "confidence_score": 0.85,
                    "source": "Heuristic Port Analyzer",
                    "description": f"Known malicious port pattern: {suspicious_ports[port_num]}",
                    "tags": ["malicious_port", "backdoor"]
                })
        except ValueError:
            pass

    return iocs


def extract_iocs_from_text(text: str) -> List[Dict[str, Any]]:
    """Extracts IP, Domain, and Hash indicators from raw log text or descriptions."""
    iocs = []
    
    # IPs
    for match in IPV4_REGEX.findall(text):
        if validate_ipv4(match):
            iocs.append({
                "value": match,
                "ioc_type": "ipv4",
                "observed_status": "observed",
                "verification_status": "unverified",
                "severity": "Medium",
                "confidence_score": 0.5,
                "source": "Text Extraction",
                "tags": ["regex_extracted"]
            })

    # SHA256
    for match in SHA256_REGEX.findall(text):
        iocs.append({
            "value": match.lower(),
            "ioc_type": "sha256",
            "observed_status": "observed",
            "verification_status": "suspicious",
            "severity": "High",
            "confidence_score": 0.8,
            "source": "Text Extraction",
            "tags": ["file_hash", "regex_extracted"]
        })

    # Deduplicate by value
    unique_iocs = {}
    for item in iocs:
        unique_iocs[item["value"]] = item
    return list(unique_iocs.values())
