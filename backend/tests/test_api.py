import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_dashboard_endpoint(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "total_alerts" in data
    assert "attack_class_distribution" in data
    assert "detection_rate_pct" in data

def test_prediction_flow_endpoint(client):
    payload = {
        "src_ip": "45.33.32.156",
        "dst_ip": "10.0.0.1",
        "dst_port": 80,
        "protocol": "TCP",
        "flow_duration": 4.5,
        "fwd_pkts": 1200.0,
        "bwd_pkts": 2.0,
        "fwd_bytes": 72000.0,
        "bwd_bytes": 80.0
    }
    res = client.post("/api/predictions/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "predicted_class" in data
    assert "confidence" in data
    assert "risk_score" in data
    assert "feature_importances" in data
    assert len(data["feature_importances"]) > 0

def test_alerts_lifecycle_endpoint(client):
    # Fetch alerts
    res = client.get("/api/alerts")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) > 0
    
    first_id = items[0]["id"]

    # 1. Unauthenticated attempt must be rejected with 401 Unauthorized (Auth Enforcement)
    unauth_res = client.patch(f"/api/alerts/{first_id}", json={
        "status": "Investigating"
    })
    assert unauth_res.status_code == 401

    # 2. Authenticated update must succeed
    auth_headers = {"Authorization": "Bearer dev-analyst-token"}
    patch_res = client.patch(
        f"/api/alerts/{first_id}",
        headers=auth_headers,
        json={
            "status": "Investigating",
            "new_note": "Analyst inspecting packet captures"
        }
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "Investigating"


def test_cti_iocs_and_enrichment(client):
    res = client.get("/api/iocs")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) > 0

    # Enrich IP
    enrich_res = client.post("/api/cti/enrich?target=45.33.32.156")
    assert enrich_res.status_code == 200
    assert "enrichment" in enrich_res.json()
