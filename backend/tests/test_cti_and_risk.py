import pytest
from app.cti.ioc_extractor import extract_iocs_from_flow, extract_iocs_from_text, validate_ipv4
from app.cti.risk_scoring import calculate_risk_score
from app.cti.mitre_mapper import map_attack_to_mitre
from app.cti.stix_export import export_iocs_to_stix
from app.models.cti import IOC
from app.models.alert import Alert

def test_ioc_extraction_and_normalization():
    flow = {
        "src_ip": "185.220.101.5",
        "dst_ip": "10.0.0.1",
        "dst_port": 4444
    }
    iocs = extract_iocs_from_flow(flow)
    assert len(iocs) >= 2
    
    values = [i["value"] for i in iocs]
    assert "185.220.101.5" in values
    assert "port:4444" in values

def test_risk_scoring_formula():
    # Benign flow
    score_b, sev_b, _ = calculate_risk_score("Benign", 0.95)
    assert score_b <= 20.0
    assert sev_b == "Informational"

    # High severity attack
    score_d, sev_d, _ = calculate_risk_score("DoS", 0.92, dst_port=80, reputation_score=90)
    assert score_d >= 70.0
    assert sev_d in ["High", "Critical"]

def test_mitre_mapping():
    m = map_attack_to_mitre("PortScan")
    assert m["technique_id"] == "T1046"
    assert m["tactic"] == "Discovery"

    m_dos = map_attack_to_mitre("DoS")
    assert m_dos["technique_id"] == "T1498"
    assert m_dos["tactic"] == "Impact"

def test_stix_export_bundle_format():
    sample_ioc = IOC(
        value="45.33.32.156",
        ioc_type="ipv4",
        observed_status="flagged",
        verification_status="confirmed_malicious",
        confidence_score=0.9
    )
    bundle = export_iocs_to_stix([sample_ioc], [])
    assert bundle["type"] == "bundle"
    assert bundle["spec_version"] == "2.1"
    assert len(bundle["objects"]) >= 2
