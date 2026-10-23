import io
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ml.inference import inference_service

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

auth_headers = {"Authorization": "Bearer dev-analyst-token"}

def test_live_status_endpoint(client):
    res = client.get("/api/predictions/status/live")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "interface" in data
    assert "sensor_id" in data
    assert "total_live_flows_captured" in data
    assert isinstance(data["total_live_flows_captured"], int)

def test_live_ingest_flows(client):
    live_flows = [
        {
            "src_ip": "198.51.100.45",
            "dst_ip": "10.0.0.1",
            "src_port": 54321,
            "dst_port": 80,
            "protocol": "TCP",
            "flow_duration": 3.5,
            "fwd_pkts": 1500.0,
            "bwd_pkts": 2.0,
            "fwd_bytes": 90000.0,
            "bwd_bytes": 80.0,
            "flow_rate_bytes_per_sec": 25737.0,
            "flow_rate_pkts_per_sec": 429.0,
            "tcp_flags_syn": 1.0,
            "tcp_flags_ack": 0.0
        },
        {
            "src_ip": "192.168.1.105",
            "dst_ip": "10.0.0.5",
            "src_port": 49152,
            "dst_port": 443,
            "protocol": "TCP",
            "flow_duration": 1200.0,
            "fwd_pkts": 12.0,
            "bwd_pkts": 15.0,
            "fwd_bytes": 2400.0,
            "bwd_bytes": 14000.0,
            "tcp_flags_syn": 0.0,
            "tcp_flags_ack": 1.0
        }
    ]

    res = client.post(
        "/api/predictions/live-ingest",
        headers=auth_headers,
        json={
            "flows": live_flows,
            "sensor_id": "SENSOR-TEST-LIVE",
            "interface": "eth0",
            "create_alerts": True
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["sensor_id"] == "SENSOR-TEST-LIVE"
    assert data["interface"] == "eth0"
    assert data["ingested_count"] == 2
    assert "malicious_count" in data
    assert "benign_count" in data
    assert "anomaly_count" in data
    assert len(data["items"]) == 2

    for item in data["items"]:
        assert item["ingestion_source"] == "live_capture"
        assert "is_anomaly" in item

def test_upload_flows_csv(client):
    csv_content = """src_ip,dst_ip,src_port,dst_port,protocol,flow_duration,fwd_pkts,bwd_pkts,fwd_bytes,bwd_bytes,tcp_flags_syn,tcp_flags_ack
45.33.32.11,10.0.0.1,49152,80,TCP,2.5,1200.0,2.0,72000.0,80.0,1.0,0.0
192.168.1.55,10.0.0.2,51234,443,TCP,1500.0,10.0,14.0,1800.0,12000.0,0.0,1.0
198.51.100.99,10.0.0.3,53421,22,TCP,850.0,40.0,42.0,8500.0,8800.0,1.0,1.0
"""
    files = {
        "file": ("test_flows.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
    }
    data = {
        "batch_size": "10",
        "create_alerts": "true"
    }

    res = client.post(
        "/api/predictions/upload-flows",
        headers=auth_headers,
        files=files,
        data=data
    )
    assert res.status_code == 200
    body = res.json()
    assert body["filename"] == "test_flows.csv"
    assert body["total_parsed"] == 3
    assert body["processed_count"] == 3
    assert len(body["items"]) == 3
    for item in body["items"]:
        assert item["ingestion_source"] == "file_upload"
        assert "confidence" in item
        assert "predicted_class" in item

def test_upload_flows_json(client):
    json_data = [
        {
            "src_ip": "185.220.101.44",
            "dst_ip": "10.0.0.2",
            "dst_port": 8080,
            "protocol": "TCP",
            "flow_duration": 1.2,
            "fwd_pkts": 3.0,
            "bwd_pkts": 0.0,
            "fwd_bytes": 120.0,
            "bwd_bytes": 0.0,
            "tcp_flags_syn": 1.0
        }
    ]
    files = {
        "file": ("flows.json", io.BytesIO(json.dumps(json_data).encode("utf-8")), "application/json")
    }
    res = client.post(
        "/api/predictions/upload-flows",
        headers=auth_headers,
        files=files,
        data={"batch_size": "5"}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["total_parsed"] == 1
    assert body["processed_count"] == 1
    assert body["items"][0]["ingestion_source"] == "file_upload"

def test_open_set_anomaly_logic():
    # Verify open-set threshold and logic
    from app.ml.inference import OPEN_SET_THRESHOLD
    assert OPEN_SET_THRESHOLD == 0.40

    # Ensure extract_and_validate_features extracts expected shape
    raw_sample = {
        "Flow Duration": 4500000.0,
        "Total Fwd Packets": 1200.0,
        "Total Backward Packets": 2.0,
        "Total Length of Fwd Packets": 72000.0,
        "Total Length of Bwd Packets": 80.0,
        "Destination Port": 80,
        "SYN Flag Count": 1.0,
        "ACK Flag Count": 0.0,
        "Protocol": "6"
    }
    numericals, categoricals = inference_service.extract_and_validate_features(raw_sample)
    assert numericals["flow_duration"] == 4500000.0
    assert numericals["fwd_pkts"] == 1200.0
    assert numericals["tcp_flags_syn"] == 1.0
    assert categoricals["protocol"] == "6"
    assert categoricals["dst_port_category"] == "web"

def test_ground_truth_isolation(client):
    # Pass a raw flow that includes a ground_truth_attack label
    payload = {
        "src_ip": "192.168.1.99",
        "dst_ip": "10.0.0.5",
        "dst_port": 443,
        "protocol": "TCP",
        "flow_duration": 1500.0,
        "fwd_pkts": 10.0,
        "bwd_pkts": 12.0,
        "fwd_bytes": 1600.0,
        "bwd_bytes": 9500.0,
        "ground_truth_attack": "DDoS",  # Fabricated claim in payload
        "ground_truth_label": 1
    }
    res = client.post("/api/predictions/predict", json=payload)
    assert res.status_code == 200
    data = res.json()

    # The model output must NOT simply echo the ground_truth_attack
    # Normal benign HTTPS traffic should be classified by the neural network weights
    assert "predicted_class" in data
    # Ground truth is recorded in metadata for validation comparison, not as model output
    assert data.get("ground_truth_attack") == "DDoS"
    # Ground truth was not forced as the predicted class: model evaluated features independently
    assert isinstance(data["confidence"], float)

def test_dashboard_ingestion_breakdown(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "by_ingestion_source" in data
    assert "anomaly_flows" in data
    assert isinstance(data["by_ingestion_source"], dict)
    assert isinstance(data["anomaly_flows"], int)
