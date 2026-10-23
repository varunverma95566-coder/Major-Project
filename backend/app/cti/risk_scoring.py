"""Risk Scoring Engine.

Computes a normalized risk score (0 to 100) and severity rating
using a multi-factor formula combining model confidence, attack impact weight,
indicator reputation, port criticality, and repetition factor.
"""

from typing import Dict, Any, Tuple, Optional

# Base severity weights by attack category (0 - 100)
ATTACK_SEVERITY_WEIGHTS: Dict[str, float] = {
    "Benign": 0.0,
    "PortScan": 45.0,
    "scanning": 45.0,
    "Fuzzers": 50.0,
    "Reconnaissance": 45.0,
    "Analysis": 45.0,
    "BruteForce": 70.0,
    "FTP-BruteForce": 70.0,
    "SSH-Bruteforce": 75.0,
    "password": 70.0,
    "Brute_Force_-Web": 70.0,
    "Brute_Force_-XSS": 75.0,
    "DoS": 80.0,
    "DoS_attacks-GoldenEye": 80.0,
    "DoS_attacks-Hulk": 80.0,
    "DoS_attacks-SlowHTTPTest": 75.0,
    "DoS_attacks-Slowloris": 75.0,
    "DDoS": 85.0,
    "DDOS_attack-HOIC": 85.0,
    "DDoS_attacks-LOIC-HTTP": 85.0,
    "DDOS_attack-LOIC-UDP": 85.0,
    "injection": 85.0,
    "SQL_Injection": 85.0,
    "xss": 75.0,
    "Exploits": 90.0,
    "Shellcode": 90.0,
    "Infilteration": 80.0,
    "Bot": 85.0,
    "Botnet": 85.0,
    "Backdoor": 95.0,
    "mitm": 85.0,
    "ransomware": 95.0,
    "Worms": 90.0,
    "Theft": 75.0,
    "Generic": 55.0,
    "Generic_Malicious": 60.0,
    "Unknown / Suspicious Anomaly": 65.0,
}

def get_base_severity_weight(attack_class: str) -> float:
    if attack_class in ATTACK_SEVERITY_WEIGHTS:
        return ATTACK_SEVERITY_WEIGHTS[attack_class]
    c_lower = attack_class.lower()
    if "ddos" in c_lower or "hoic" in c_lower or "loic" in c_lower:
        return 85.0
    if "dos" in c_lower:
        return 80.0
    if "backdoor" in c_lower or "ransom" in c_lower or "worm" in c_lower or "bot" in c_lower:
        return 90.0
    if "inject" in c_lower or "exploit" in c_lower or "shell" in c_lower:
        return 85.0
    if "brute" in c_lower or "password" in c_lower:
        return 75.0
    if "scan" in c_lower or "recon" in c_lower or "probe" in c_lower:
        return 45.0
    if "anomaly" in c_lower or "suspicious" in c_lower:
        return 65.0
    return 60.0

# Critical target port modifiers
CRITICAL_PORTS: Dict[int, float] = {
    22: 1.15,   # SSH
    3389: 1.20, # RDP
    445: 1.25,  # SMB
    80: 1.05,   # HTTP
    443: 1.05,  # HTTPS
    53: 1.10,   # DNS
    8080: 1.05
}


def calculate_risk_score(
    predicted_class: str,
    confidence: float,
    dst_port: Optional[int] = None,
    reputation_score: Optional[int] = None,
    frequency_count: int = 1
) -> Tuple[float, str, str]:
    """
    Computes (risk_score, severity, rationale).
    
    Formula:
    Risk = (Base_Category_Weight * 0.50) + (Model_Confidence * 30) + (Reputation_Contribution * 0.15) + Port_Modifier
    """
    if predicted_class == "Benign" and confidence > 0.6:
        return 5.0, "Informational", "Normal baseline operational traffic."

    # 1. Base attack weight
    base_weight = get_base_severity_weight(predicted_class)

    # 2. Confidence scaling (0.0 to 1.0 -> 0 to 30 pts)
    confidence_pts = min(max(confidence, 0.0), 1.0) * 30.0

    # 3. Reputation scaling (0 to 100 -> 0 to 15 pts)
    rep = float(reputation_score or 0)
    reputation_pts = (rep / 100.0) * 15.0

    # 4. Port modifier
    port_mod = 1.0
    if dst_port and int(dst_port) in CRITICAL_PORTS:
        port_mod = CRITICAL_PORTS[int(dst_port)]

    # 5. Frequency surge (e.g. repeated attempts boost score by up to 10 pts)
    freq_boost = min((frequency_count - 1) * 2.0, 10.0)

    # Combine components
    raw_score = ((base_weight * 0.50) + confidence_pts + reputation_pts + freq_boost) * port_mod
    normalized_score = round(min(max(raw_score, 0.0), 100.0), 1)

    # Assign Severity
    if normalized_score >= 90.0:
        severity = "Critical"
    elif normalized_score >= 70.0:
        severity = "High"
    elif normalized_score >= 40.0:
        severity = "Medium"
    elif normalized_score >= 20.0:
        severity = "Low"
    else:
        severity = "Informational"

    rationale = (
        f"Score {normalized_score}/100 [{severity}] calculated from {predicted_class} base weight ({base_weight}), "
        f"confidence ({confidence:.2f}), reputation ({rep}), port modifier ({port_mod}x), and frequency ({frequency_count})."
    )

    return normalized_score, severity, rationale
