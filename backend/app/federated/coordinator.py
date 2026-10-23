import copy
import torch
from typing import List, Dict, Any, Tuple
from app.core.logging import logger


class FederatedCoordinator:
    def __init__(self, global_model_state: Dict[str, torch.Tensor], arch_config: Dict[str, Any]):
        self.global_state = copy.deepcopy(global_model_state)
        self.arch_config = arch_config
        self.current_round = 0

    def aggregate_fedavg(
        self,
        client_updates: List[Tuple[str, Dict[str, torch.Tensor], int]]
    ) -> Dict[str, torch.Tensor]:
        """
        Federated Averaging (FedAvg):
        Calculates weighted sum of client model weights based on client sample count.
        Validates client weights against NaN/Inf poisoning and incompatible architectures.
        Never accesses client raw training datasets.
        """
        valid_updates = []
        for client_id, client_weights, sample_count in client_updates:
            if sample_count <= 0:
                logger.warning(f"Client {client_id} reported 0 or negative samples; skipping update.")
                continue

            # Validate parameter architecture and values
            is_valid = True
            for key, global_tensor in self.global_state.items():
                if key not in client_weights:
                    logger.warning(f"Client {client_id} missing model layer '{key}'; rejecting update.")
                    is_valid = False
                    break
                
                c_tensor = client_weights[key]
                if c_tensor.shape != global_tensor.shape:
                    logger.warning(f"Client {client_id} layer '{key}' shape mismatch: {c_tensor.shape} vs {global_tensor.shape}; rejecting.")
                    is_valid = False
                    break

                if torch.isnan(c_tensor).any() or torch.isinf(c_tensor).any():
                    logger.warning(f"Client {client_id} submitted NaN/Inf tensors in '{key}'; rejecting suspicious/corrupted update.")
                    is_valid = False
                    break

            if is_valid:
                valid_updates.append((client_id, client_weights, sample_count))

        total_samples = sum(sample_count for _, _, sample_count in valid_updates)
        if total_samples == 0:
            logger.warning("No valid client updates received in federated round. Global weights retained.")
            return self.global_state

        aggregated_state = {}
        for key in self.global_state.keys():
            aggregated_tensor = torch.zeros_like(self.global_state[key], dtype=torch.float32)
            for _, client_weights, sample_count in valid_updates:
                weight = sample_count / total_samples
                aggregated_tensor += client_weights[key].to(torch.float32) * weight
            aggregated_state[key] = aggregated_tensor

        self.global_state = aggregated_state
        self.current_round += 1
        return self.global_state

