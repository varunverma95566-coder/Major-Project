"""MITRE ATT&CK Mapping Module.

Grounds detected network attack patterns in MITRE ATT&CK Enterprise Matrix (v14.1).
Provides technique metadata, tactics, mapping rationales, and confidence weights.
"""

from typing import Dict, Any, List, Optional

MITRE_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "PortScan": {
        "technique_id": "T1046",
        "name": "Network Service Scanning",
        "tactic": "Discovery",
        "description": "Adversaries may attempt to get a listing of services running on remote hosts to identify vulnerable applications.",
        "rationale": "High rate of SYN packets targeting sequential or multiple distinct destination ports with negligible backward payloads.",
        "confidence": 0.88,
        "url": "https://attack.mitre.org/techniques/T1046/",
        "attck_version": "v14.1"
    },
    "scanning": {
        "technique_id": "T1046",
        "name": "Network Service Scanning",
        "tactic": "Discovery",
        "description": "Network scanning and host service discovery probing.",
        "rationale": "High rate of probes targeting services across ports or IP ranges.",
        "confidence": 0.88,
        "url": "https://attack.mitre.org/techniques/T1046/",
        "attck_version": "v14.1"
    },
    "Reconnaissance": {
        "technique_id": "T1595",
        "name": "Active Scanning",
        "tactic": "Reconnaissance",
        "description": "Adversaries may execute active reconnaissance scans against target infrastructure.",
        "rationale": "Systematic multi-port telemetry with exploratory payload lengths.",
        "confidence": 0.87,
        "url": "https://attack.mitre.org/techniques/T1595/",
        "attck_version": "v14.1"
    },
    "DoS": {
        "technique_id": "T1498",
        "name": "Network Denial of Service",
        "tactic": "Impact",
        "description": "Adversaries may perform Network Denial of Service attacks to degrade or block the availability of targeted resources to users.",
        "rationale": "Volumetric burst of forward packets with elevated bytes-per-second, targeting critical service ports (e.g. 80, 443).",
        "confidence": 0.90,
        "url": "https://attack.mitre.org/techniques/T1498/",
        "attck_version": "v14.1"
    },
    "DDoS": {
        "technique_id": "T1498.001",
        "name": "Direct Network Flood",
        "tactic": "Impact",
        "description": "Adversaries may conduct direct volumetric network floods using botnets to saturate service bandwidth.",
        "rationale": "Multi-source coordinated flood traffic exhibiting synchronized inter-arrival times.",
        "confidence": 0.92,
        "url": "https://attack.mitre.org/techniques/T1498/001/",
        "attck_version": "v14.1"
    },
    "DDOS_attack-HOIC": {
        "technique_id": "T1498.001",
        "name": "Direct Network Flood (HOIC)",
        "tactic": "Impact",
        "description": "High Orbit Ion Cannon HTTP volumetric flooding targeting web applications.",
        "rationale": "High-frequency HTTP request bursts designed to exhaust web application thread pools.",
        "confidence": 0.93,
        "url": "https://attack.mitre.org/techniques/T1498/001/",
        "attck_version": "v14.1"
    },
    "DDoS_attacks-LOIC-HTTP": {
        "technique_id": "T1498.001",
        "name": "Direct Network Flood (LOIC-HTTP)",
        "tactic": "Impact",
        "description": "Low Orbit Ion Cannon coordinated application flood over HTTP.",
        "rationale": "Mass synchronized HTTP GET/POST connection requests.",
        "confidence": 0.91,
        "url": "https://attack.mitre.org/techniques/T1498/001/",
        "attck_version": "v14.1"
    },
    "DDOS_attack-LOIC-UDP": {
        "technique_id": "T1498.001",
        "name": "Direct Network Flood (LOIC-UDP)",
        "tactic": "Impact",
        "description": "Volumetric UDP packet flooding saturating network interfaces.",
        "rationale": "Excessive high-speed UDP datagram transmission to random destination ports.",
        "confidence": 0.92,
        "url": "https://attack.mitre.org/techniques/T1498/001/",
        "attck_version": "v14.1"
    },
    "DoS_attacks-SlowHTTPTest": {
        "technique_id": "T1499.003",
        "name": "Endpoint DoS (Slowloris/SlowHTTP)",
        "tactic": "Impact",
        "description": "Low-and-slow application resource starvation through incomplete HTTP requests.",
        "rationale": "Extended flow durations with persistent keep-alive headers and low packet rates.",
        "confidence": 0.89,
        "url": "https://attack.mitre.org/techniques/T1499/003/",
        "attck_version": "v14.1"
    },
    "DoS_attacks-Hulk": {
        "technique_id": "T1498.001",
        "name": "Direct Network Flood (HULK)",
        "tactic": "Impact",
        "description": "HTTP Unbearable Load King DoS attack with obfuscated request headers.",
        "rationale": "Bypasses edge caching through randomized user agents and unique query parameters.",
        "confidence": 0.90,
        "url": "https://attack.mitre.org/techniques/T1498/001/",
        "attck_version": "v14.1"
    },
    "DoS_attacks-GoldenEye": {
        "technique_id": "T1499",
        "name": "Endpoint Denial of Service (GoldenEye)",
        "tactic": "Impact",
        "description": "HTTP Keep-Alive and No-Cache flooding exhausting server connection pools.",
        "rationale": "Dual Keep-Alive exhaustion flows without socket termination.",
        "confidence": 0.89,
        "url": "https://attack.mitre.org/techniques/T1499/",
        "attck_version": "v14.1"
    },
    "DoS_attacks-Slowloris": {
        "technique_id": "T1499.003",
        "name": "Slowloris Application Exhaustion",
        "tactic": "Impact",
        "description": "Holds web server connections open indefinitely by sending partial HTTP headers.",
        "rationale": "Unusually long flow duration with minimal periodic byte transmissions.",
        "confidence": 0.91,
        "url": "https://attack.mitre.org/techniques/T1499/003/",
        "attck_version": "v14.1"
    },
    "BruteForce": {
        "technique_id": "T1110",
        "name": "Brute Force",
        "tactic": "Credential Access",
        "description": "Adversaries may use brute force techniques to attempt credential guessing against authentication services.",
        "rationale": "Repeated connection attempts to administrative authentication ports (e.g. 22 SSH, 3389 RDP) with continuous payload exchange.",
        "confidence": 0.85,
        "url": "https://attack.mitre.org/techniques/T1110/",
        "attck_version": "v14.1"
    },
    "password": {
        "technique_id": "T1110.001",
        "name": "Password Guessing",
        "tactic": "Credential Access",
        "description": "Systematic automated password guessing against network login services.",
        "rationale": "Repeated login handshake flows over authentication ports.",
        "confidence": 0.87,
        "url": "https://attack.mitre.org/techniques/T1110/001/",
        "attck_version": "v14.1"
    },
    "SSH-Bruteforce": {
        "technique_id": "T1110.001",
        "name": "SSH Password Guessing",
        "tactic": "Credential Access",
        "description": "Automated brute-force authentication attempts against Secure Shell (port 22).",
        "rationale": "Bursts of SSH protocol negotiation flows with rapid disconnect/reconnect sequences.",
        "confidence": 0.92,
        "url": "https://attack.mitre.org/techniques/T1110/001/",
        "attck_version": "v14.1"
    },
    "FTP-BruteForce": {
        "technique_id": "T1110.001",
        "name": "FTP Password Guessing",
        "tactic": "Credential Access",
        "description": "Automated credential attacks targeting File Transfer Protocol (port 21).",
        "rationale": "Sequential authentication handshake exchanges on port 21.",
        "confidence": 0.90,
        "url": "https://attack.mitre.org/techniques/T1110/001/",
        "attck_version": "v14.1"
    },
    "xss": {
        "technique_id": "T1059.007",
        "name": "Cross-Site Scripting (XSS)",
        "tactic": "Execution",
        "description": "Client-side script execution attacks injection via web requests.",
        "rationale": "Web traffic payloads carrying encoded script tags and event handlers.",
        "confidence": 0.86,
        "url": "https://attack.mitre.org/techniques/T1059/007/",
        "attck_version": "v14.1"
    },
    "injection": {
        "technique_id": "T1190",
        "name": "Command/Code Injection",
        "tactic": "Initial Access",
        "description": "Injection of code or commands into public-facing applications.",
        "rationale": "HTTP request payloads with escape characters and database or shell metacharacters.",
        "confidence": 0.89,
        "url": "https://attack.mitre.org/techniques/T1190/",
        "attck_version": "v14.1"
    },
    "SQL_Injection": {
        "technique_id": "T1190",
        "name": "SQL Injection",
        "tactic": "Initial Access",
        "description": "Adversaries inject SQL control clauses into input fields to manipulate database queries.",
        "rationale": "Payload signatures containing SQL syntax keywords (UNION, SELECT, OR 1=1).",
        "confidence": 0.93,
        "url": "https://attack.mitre.org/techniques/T1190/",
        "attck_version": "v14.1"
    },
    "Bot": {
        "technique_id": "T1071",
        "name": "Botnet C2 Communication",
        "tactic": "Command and Control",
        "description": "Automated bot telemetry and command-and-control beaconing.",
        "rationale": "Periodic heartbeat flows to remote external nodes with fixed packet lengths.",
        "confidence": 0.87,
        "url": "https://attack.mitre.org/techniques/T1071/",
        "attck_version": "v14.1"
    },
    "Botnet": {
        "technique_id": "T1071",
        "name": "Application Layer Protocol",
        "tactic": "Command and Control",
        "description": "Adversaries may communicate using application layer protocols to avoid detection by blending with normal network traffic.",
        "rationale": "Periodic beaconing flows with uniform packet sizes and recurring connection intervals directed at known C2 infrastructure.",
        "confidence": 0.86,
        "url": "https://attack.mitre.org/techniques/T1071/",
        "attck_version": "v14.1"
    },
    "Infilteration": {
        "technique_id": "T1203",
        "name": "Exploitation for Client Execution / Infiltration",
        "tactic": "Execution",
        "description": "Adversaries exploit client vulnerabilities to compromise internal network segments.",
        "rationale": "Unusual internal lateral movement and payload transfer across endpoints.",
        "confidence": 0.84,
        "url": "https://attack.mitre.org/techniques/T1203/",
        "attck_version": "v14.1"
    },
    "Backdoor": {
        "technique_id": "T1133",
        "name": "External Remote Services / Backdoor",
        "tactic": "Persistence",
        "description": "Persistent interactive shell or tunnel installed for remote unauthorized access.",
        "rationale": "Long-lived asymmetric flows with periodic interactive command payloads.",
        "confidence": 0.88,
        "url": "https://attack.mitre.org/techniques/T1133/",
        "attck_version": "v14.1"
    },
    "Exploits": {
        "technique_id": "T1190",
        "name": "Exploit Public-Facing Application",
        "tactic": "Initial Access",
        "description": "Adversaries may attempt to exploit vulnerabilities in Internet-facing applications or web servers.",
        "rationale": "Abnormal payload length distribution and specific application layer request anomalies.",
        "confidence": 0.80,
        "url": "https://attack.mitre.org/techniques/T1190/",
        "attck_version": "v14.1"
    },
    "Fuzzers": {
        "technique_id": "T1595.002",
        "name": "Vulnerability Scanning",
        "tactic": "Reconnaissance",
        "description": "Adversaries may scan for vulnerabilities in public-facing applications using automated fuzzing.",
        "rationale": "High frequency of varied length malformed requests aimed at software discovery.",
        "confidence": 0.82,
        "url": "https://attack.mitre.org/techniques/T1595/002/",
        "attck_version": "v14.1"
    },
    "ransomware": {
        "technique_id": "T1486",
        "name": "Data Encrypted for Impact (Ransomware)",
        "tactic": "Impact",
        "description": "High-volume file transfer and encryption signaling traffic across shares.",
        "rationale": "Rapid asymmetric burst of SMB/NFS file read/write operations.",
        "confidence": 0.90,
        "url": "https://attack.mitre.org/techniques/T1486/",
        "attck_version": "v14.1"
    },
    "mitm": {
        "technique_id": "T1557",
        "name": "Adversary-in-the-Middle (MitM)",
        "tactic": "Credential Access",
        "description": "ARP/DNS poisoning and traffic interception between communication endpoints.",
        "rationale": "Inconsistent MAC address routing and anomalous ICMP redirect messages.",
        "confidence": 0.85,
        "url": "https://attack.mitre.org/techniques/T1557/",
        "attck_version": "v14.1"
    },
    "Shellcode": {
        "technique_id": "T1059",
        "name": "Command and Scripting Interpreter (Shellcode)",
        "tactic": "Execution",
        "description": "Transmission of raw shellcode bytecode payloads to exploit memory buffers.",
        "rationale": "High density of NOP sled bytes (0x90) and raw binary executable opcodes.",
        "confidence": 0.89,
        "url": "https://attack.mitre.org/techniques/T1059/",
        "attck_version": "v14.1"
    },
    "Theft": {
        "technique_id": "T1048",
        "name": "Exfiltration Over Alternative Protocol",
        "tactic": "Exfiltration",
        "description": "Unauthorized exfiltration of sensitive data to external actor-controlled servers.",
        "rationale": "Unusual outbound data transfer volumes with elevated byte-to-packet ratios.",
        "confidence": 0.84,
        "url": "https://attack.mitre.org/techniques/T1048/",
        "attck_version": "v14.1"
    },
    "Analysis": {
        "technique_id": "T1592",
        "name": "Gather Victim Host Information",
        "tactic": "Reconnaissance",
        "description": "Target probing to discover operating system versions, open ports, and patch levels.",
        "rationale": "Varied banner grabbing queries targeting common network management services.",
        "confidence": 0.83,
        "url": "https://attack.mitre.org/techniques/T1592/",
        "attck_version": "v14.1"
    },
    "Worms": {
        "technique_id": "T1570",
        "name": "Lateral Tool Transfer (Worm Propagation)",
        "tactic": "Lateral Movement",
        "description": "Self-propagating malware spreading across internal subnet ranges via exploits.",
        "rationale": "Automated sequential connection bursts to subnet addresses on vulnerability ports.",
        "confidence": 0.88,
        "url": "https://attack.mitre.org/techniques/T1570/",
        "attck_version": "v14.1"
    },
    "Generic": {
        "technique_id": "T1040",
        "name": "Network Sniffing / Malicious Traffic",
        "tactic": "Credential Access",
        "description": "Generic anomalous network telemetry exceeding statistical benign flow thresholds.",
        "rationale": "Flow features deviate substantially from baseline operational profiles.",
        "confidence": 0.72,
        "url": "https://attack.mitre.org/techniques/T1040/",
        "attck_version": "v14.1"
    },
    "Generic_Malicious": {
        "technique_id": "T1040",
        "name": "Network Sniffing / Malicious Traffic",
        "tactic": "Credential Access",
        "description": "General malicious network telemetry exceeding statistical benign flow thresholds.",
        "rationale": "Flow features deviate substantially from baseline operational profiles.",
        "confidence": 0.70,
        "url": "https://attack.mitre.org/techniques/T1040/",
        "attck_version": "v14.1"
    }
}


def map_attack_to_mitre(attack_category: str, flow_evidence: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Resolves an attack category to its corresponding MITRE ATT&CK technique."""
    entry = MITRE_KNOWLEDGE_BASE.get(attack_category)
    if not entry:
        for k in MITRE_KNOWLEDGE_BASE:
            if k.lower() in attack_category.lower() or attack_category.lower() in k.lower():
                entry = MITRE_KNOWLEDGE_BASE[k]
                break

    if not entry:
        entry = MITRE_KNOWLEDGE_BASE["Generic_Malicious"]

    result = entry.copy()
    if flow_evidence:
        result["supporting_evidence"] = {
            "dst_port": flow_evidence.get("dst_port"),
            "protocol": flow_evidence.get("protocol"),
            "flow_rate_pkts_per_sec": flow_evidence.get("flow_rate_pkts_per_sec")
        }
    return result


def get_all_mitre_techniques() -> List[Dict[str, Any]]:
    return list(MITRE_KNOWLEDGE_BASE.values())
