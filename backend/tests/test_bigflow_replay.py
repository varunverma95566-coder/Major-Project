import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.datasets.bigflow_loader import BigFlowDataLoader, BIGFLOW_CATEGORY_PARTITION_MAP

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_bigflow_categories_metadata_endpoint(client):
    """Validates that all 32 real BigFlow-NIDS categories are exposed with exact model-support indicators."""
    res = client.get("/api/predictions/bigflow/categories")
    assert res.status_code == 200
    data = res.json()

    assert data["total_categories"] == 32
    assert data["model_supported_count"] == 24
    assert data["unsupported_count"] == 8
    assert data["active_model_name"] is not None

    categories = data["categories"]
    assert len(categories) == 32

    cat_map = {c["name"]: c for c in categories}
    assert "Benign" in cat_map
    assert "DDoS" in cat_map
    assert "Worms" in cat_map
    assert "SQL_Injection" in cat_map
    assert "ransomware" in cat_map

    # Check model-supported vs unsupported annotations
    assert cat_map["DDoS"]["is_supported"] is True
    assert cat_map["Benign"]["is_supported"] is True
    assert cat_map["Worms"]["is_supported"] is False
    assert cat_map["SQL_Injection"]["is_supported"] is False
    assert "retraining required" in cat_map["Worms"]["unsupported_reason"].lower()


def test_bigflow_replay_supported_category(client):
    """Validates streaming real representative flows for a model-supported attack category (DDoS)."""
    payload = {
        "category": "DDoS",
        "batch_size": 2,
        "create_alerts": False
    }
    res = client.post("/api/predictions/replay-bigflow", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["category_requested"] == "DDoS"
    assert data["processed_count"] >= 1
    assert len(data["items"]) == data["processed_count"]

    first = data["items"][0]
    assert first["ground_truth_attack"] == "DDoS"
    assert first["is_ground_truth_malicious"] is True
    assert first["model_supported"] is True
    assert "BigFlow-NIDS-V2" in first["dataset_source"]
    assert first["predicted_class"] is not None
    assert 0.0 <= first["confidence"] <= 1.0
    assert 0.0 <= first["risk_score"] <= 100.0
    assert first["inference_time_ms"] > 0
    assert len(first["feature_importances"]) > 0


def test_bigflow_replay_unsupported_category_graceful_handling(client):
    """Validates that replaying an unsupported category (e.g. Worms) correctly flags model_supported=False and returns retraining notice."""
    payload = {
        "category": "Worms",
        "batch_size": 1,
        "create_alerts": False
    }
    res = client.post("/api/predictions/replay-bigflow", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["category_requested"] == "Worms"
    assert data["processed_count"] >= 1

    item = data["items"][0]
    assert item["ground_truth_attack"] == "Worms"
    assert item["model_supported"] is False
    assert item["unsupported_warning"] is not None
    assert "Retraining required" in item["unsupported_warning"]
    # Model still performs inference and predicts closest latent class
    assert item["predicted_class"] is not None
    assert item["confidence"] > 0.0


def test_bigflow_replay_benign_flows(client):
    """Validates streaming Benign traffic from BigFlow-NIDS."""
    payload = {
        "category": "Benign",
        "batch_size": 2,
        "create_alerts": False
    }
    res = client.post("/api/predictions/replay-bigflow", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["category_requested"] == "Benign"
    assert data["processed_count"] >= 1
    assert data["items"][0]["ground_truth_attack"] == "Benign"
    assert data["items"][0]["is_ground_truth_malicious"] is False


def test_bigflow_replay_invalid_category_returns_404(client):
    """Validates that non-existent category returns a descriptive 404."""
    payload = {
        "category": "NonExistentAttackCategory999",
        "batch_size": 2
    }
    res = client.post("/api/predictions/replay-bigflow", json=payload)
    assert res.status_code == 404
    assert "No representative records found" in res.json()["detail"]


def test_bigflow_loader_partition_map_integrity():
    """Validates that the 32 categories in the partition map cover all expected BigFlow-NIDS classes."""
    assert len(BIGFLOW_CATEGORY_PARTITION_MAP) == 32
    for cat, part_idx in BIGFLOW_CATEGORY_PARTITION_MAP.items():
        assert isinstance(cat, str)
        assert 0 <= part_idx <= 5  # Primary partitions 0 through 5 contain all 32 classes
