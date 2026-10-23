"""Federated Learning Simulation Service.

Manages 3 simulated participating organizations:
1. Org-A (FinBank Cyber Defense)
2. Org-B (MedHealth SOC)
3. Org-C (CloudTel ISP)

Executes privacy-preserving federated rounds and persists results.
"""

import os
import json
import torch
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.federated import FederatedClient, FederatedRound
from app.datasets.preprocessor import FlowPreprocessor
from app.federated.client import FederatedClientNode
from app.federated.coordinator import FederatedCoordinator
from app.ml.flow_transformer import FlowTransformer


def initialize_federated_environment(db: Session, base_model_name: str = "flow_transformer_v1") -> bool:
    """Prepares simulated client nodes in the database if not present."""
    existing_clients = db.query(FederatedClient).all()
    if existing_clients:
        return True

    clients_data = [
        {
            "client_id": "client_fin_01",
            "name": "FinBank Financial SOC",
            "organization": "Global Finance Corp",
            "industry_sector": "Banking & Finance",
            "dataset_name": "NF-UNSW-NB15-v2 (Partition A - Financial NetFlow)",
            "local_sample_count": 180,
            "status": "active",
            "local_accuracy": 0.91,
            "local_loss": 0.28
        },
        {
            "client_id": "client_med_02",
            "name": "MedHealth Hospital Network",
            "organization": "National Health Alliance",
            "industry_sector": "Healthcare",
            "dataset_name": "NF-BoT-IoT-v2 (Partition B - Medical IoT)",
            "local_sample_count": 150,
            "status": "active",
            "local_accuracy": 0.88,
            "local_loss": 0.32
        },
        {
            "client_id": "client_tel_03",
            "name": "CloudTel Core Network",
            "organization": "Apex Telecommunications",
            "industry_sector": "Telecommunications",
            "dataset_name": "Edge-IIoTset (Partition C - Carrier Backbone)",
            "local_sample_count": 170,
            "status": "active",
            "local_accuracy": 0.93,
            "local_loss": 0.22
        }
    ]

    for c in clients_data:
        client_obj = FederatedClient(**c)
        db.add(client_obj)

    # Seed baseline round 1
    round_1 = FederatedRound(
        round_number=1,
        status="completed",
        aggregation_strategy="FedAvg",
        participating_clients=["client_fin_01", "client_med_02", "client_tel_03"],
        total_samples=500,
        global_accuracy_before=0.86,
        global_accuracy_after=0.91,
        global_loss_before=0.34,
        global_loss_after=0.25,
        client_metrics={
            "client_fin_01": {"samples": 180, "accuracy": 0.91, "weight": 0.36},
            "client_med_02": {"samples": 150, "accuracy": 0.88, "weight": 0.30},
            "client_tel_03": {"samples": 170, "accuracy": 0.93, "weight": 0.34}
        }
    )
    db.add(round_1)
    db.commit()
    logger.info("Initialized simulated federated learning nodes.")
    return True


def run_federated_round(
    db: Session,
    base_model_name: str = "flow_transformer_v1",
    client_ids: Optional[List[str]] = None,
    local_epochs: int = 1
) -> Dict[str, Any]:
    """Executes a real simulated federated learning aggregation round."""
    # If base model name not present or missing artifacts, check active model
    model_dir = os.path.join(settings.ARTIFACTS_DIR, base_model_name)
    if not os.path.exists(model_dir):
        from app.models.ml_model import MLModel
        active_m = db.query(MLModel).filter(MLModel.is_active == True).first()
        if active_m and os.path.exists(os.path.join(settings.ARTIFACTS_DIR, active_m.name)):
            base_model_name = active_m.name
            model_dir = os.path.join(settings.ARTIFACTS_DIR, base_model_name)

    weights_path = os.path.join(model_dir, "weights.pt")
    meta_path = os.path.join(model_dir, "metadata.json")
    prep_path = os.path.join(model_dir, "preprocessor.json")

    if not (os.path.exists(weights_path) and os.path.exists(meta_path) and os.path.exists(prep_path)):
        raise RuntimeError("Base FlowTransformer model must be trained before launching federated simulation rounds.")

    with open(meta_path, "r") as f:
        meta = json.load(f)
    arch = meta["architecture_config"]
    preprocessor = FlowPreprocessor.load(prep_path)
    
    # Safe deserialization (CWE-502)
    global_weights = torch.load(weights_path, map_location="cpu", weights_only=True)
    coordinator = FederatedCoordinator(global_weights, arch)

    # Load dataset partition
    sample_csv = os.path.join(settings.SAMPLE_DATASETS_DIR, "nf_unsw_nb15_v2_sample.csv")
    if not os.path.exists(sample_csv):
        raise RuntimeError(f"Sample dataset required for federated simulation not found at {sample_csv}")
    df = pd.read_csv(sample_csv)
    
    # Partition data among 3 clients
    splits = np.array_split(df, 3)
    clients_info = [
        ("client_fin_01", "FinBank Financial SOC", "Finance", splits[0]),
        ("client_med_02", "MedHealth Hospital Network", "Healthcare", splits[1]),
        ("client_tel_03", "CloudTel Core Network", "Telecom", splits[2])
    ]

    selected_ids = client_ids or ["client_fin_01", "client_med_02", "client_tel_03"]
    client_updates = []
    client_metrics = {}

    for cid, name, sec, partition in clients_info:
        if cid in selected_ids:
            node = FederatedClientNode(cid, name, name, sec, partition, preprocessor)
            updated_weights, acc, loss = node.train_local_epoch(global_weights, arch, local_epochs=local_epochs)
            client_updates.append((cid, updated_weights, len(partition)))
            client_metrics[cid] = {
                "samples": len(partition),
                "accuracy": acc,
                "loss": loss
            }
            # Update client in DB
            c_db = db.query(FederatedClient).filter(FederatedClient.client_id == cid).first()
            if c_db:
                c_db.local_accuracy = acc
                c_db.local_loss = loss
                c_db.current_round += 1

    # Perform FedAvg aggregation with input tensor validation
    new_global_weights = coordinator.aggregate_fedavg(client_updates)
    
    # Save updated global weights
    torch.save(new_global_weights, weights_path)

    # Record round in database
    latest_round = db.query(FederatedRound).order_by(FederatedRound.round_number.desc()).first()
    next_num = (latest_round.round_number + 1) if latest_round else 1

    total_valid_samples = sum(m["samples"] for m in client_metrics.values())
    if total_valid_samples > 0:
        computed_acc_after = round(sum(m["accuracy"] * m["samples"] for m in client_metrics.values()) / total_valid_samples, 4)
        computed_loss_after = round(sum(m["loss"] * m["samples"] for m in client_metrics.values()) / total_valid_samples, 4)
    else:
        computed_acc_after = 0.0
        computed_loss_after = 0.0

    acc_before = latest_round.global_accuracy_after if latest_round else 0.86
    loss_before = latest_round.global_loss_after if latest_round else 0.32

    round_record = FederatedRound(
        round_number=next_num,
        status="completed",
        aggregation_strategy="FedAvg",
        participating_clients=selected_ids,
        total_samples=total_valid_samples,
        global_accuracy_before=acc_before,
        global_accuracy_after=computed_acc_after,
        global_loss_before=loss_before,
        global_loss_after=computed_loss_after,
        client_metrics=client_metrics
    )
    db.add(round_record)
    db.commit()
    db.refresh(round_record)

    logger.info(f"Federated Round {next_num} completed successfully with FedAvg (Accuracy: {computed_acc_after:.4f}, Loss: {computed_loss_after:.4f}).")
    return {
        "round_number": next_num,
        "status": "completed",
        "participating_clients": selected_ids,
        "global_accuracy_after": computed_acc_after,
        "client_metrics": client_metrics
    }

