import torch
import pytest
from app.federated.coordinator import FederatedCoordinator

def test_fedavg_aggregation():
    # Setup dummy weight dictionary
    w_initial = {"layer1.weight": torch.zeros((4, 4)), "layer1.bias": torch.zeros(4)}
    coordinator = FederatedCoordinator(w_initial, {})

    # Client 1 updates weights to 1.0 (100 samples)
    w_client1 = {"layer1.weight": torch.ones((4, 4)), "layer1.bias": torch.ones(4)}
    
    # Client 2 updates weights to 3.0 (100 samples)
    w_client2 = {"layer1.weight": torch.full((4, 4), 3.0), "layer1.bias": torch.full((4,), 3.0)}

    client_updates = [
        ("c1", w_client1, 100),
        ("c2", w_client2, 100)
    ]

    aggregated = coordinator.aggregate_fedavg(client_updates)

    # Average of 1.0 and 3.0 with equal samples should be exactly 2.0
    expected = torch.full((4, 4), 2.0)
    assert torch.allclose(aggregated["layer1.weight"], expected)
    assert torch.allclose(aggregated["layer1.bias"], torch.full((4,), 2.0))
    assert coordinator.current_round == 1
