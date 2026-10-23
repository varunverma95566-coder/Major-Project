"""Simulated Federated Learning Client Organization.

Represents an independent participating institution (e.g. Bank, Hospital, Telecom).
Trains a local FlowTransformer model exclusively on its private partition of flows.
Transmits ONLY model parameter weights/deltas to the coordinator — NEVER raw data rows.
"""

import copy
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from app.ml.flow_transformer import FlowTransformer
from app.datasets.preprocessor import FlowPreprocessor


class FederatedClientNode:
    def __init__(
        self,
        client_id: str,
        name: str,
        organization: str,
        industry_sector: str,
        local_df: pd.DataFrame,
        preprocessor: FlowPreprocessor
    ):
        self.client_id = client_id
        self.name = name
        self.organization = organization
        self.industry_sector = industry_sector
        self.local_df = local_df
        self.preprocessor = preprocessor
        self.num_samples = len(local_df)

    def train_local_epoch(
        self,
        global_model_state: Dict[str, torch.Tensor],
        arch_config: Dict[str, Any],
        local_epochs: int = 1,
        learning_rate: float = 0.001
    ) -> Tuple[Dict[str, torch.Tensor], float, float]:
        """
        Receives global weights, performs local SGD training on private records,
        and returns updated weights + local accuracy + local loss.
        """
        # Instantiate local model clone
        model = FlowTransformer(
            num_numerical=arch_config["num_numerical"],
            cat_cardinalities=arch_config["cat_cardinalities"],
            num_classes=arch_config["num_classes"],
            embedding_dim=arch_config["embedding_dim"],
            num_heads=arch_config["num_heads"],
            num_layers=arch_config["num_layers"],
            feedforward_dim=arch_config.get("feedforward_dim", 128),
            dropout=arch_config.get("dropout", 0.1)
        )
        model.load_state_dict(global_model_state)
        
        # Prepare local tensors
        y_multi_s = self.local_df["Attack"] if "Attack" in self.local_df.columns else self.local_df["attack_category"]
        y_bin_s = self.local_df["Label"] if "Label" in self.local_df.columns else self.local_df["is_attack"]
        
        X_num, X_cat = self.preprocessor.transform(self.local_df)
        y_b, y_m = self.preprocessor.transform_labels(y_bin_s, y_multi_s)
        
        dataset = TensorDataset(
            torch.tensor(X_num, dtype=torch.float32),
            torch.tensor(X_cat, dtype=torch.long),
            torch.tensor(y_b, dtype=torch.float32),
            torch.tensor(y_m, dtype=torch.long)
        )
        loader = DataLoader(dataset, batch_size=32, shuffle=True)
        
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        criterion_m = nn.CrossEntropyLoss()
        criterion_b = nn.BCEWithLogitsLoss()
        
        model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for _ in range(local_epochs):
            for num_b, cat_b, y_bin_b, y_mul_b in loader:
                optimizer.zero_grad()
                l_bin, l_mul = model(num_b, cat_b)
                loss = criterion_b(l_bin, y_bin_b) + criterion_m(l_mul, y_mul_b)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                preds = torch.argmax(l_mul, dim=-1)
                correct += int((preds == y_mul_b).sum().item())
                total += len(y_mul_b)

        avg_loss = total_loss / max(len(loader), 1)
        accuracy = float(correct / max(total, 1))

        # Return updated parameters (CPU copy)
        local_weights = {k: v.cpu().detach().clone() for k, v in model.state_dict().items()}
        return local_weights, round(accuracy, 4), round(avg_loss, 4)
