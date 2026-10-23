import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON, ForeignKey
from app.core.database import Base

class FederatedClient(Base):
    __tablename__ = "federated_clients"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g. client_fin_01
    name = Column(String(100), nullable=False)
    organization = Column(String(100), nullable=False)
    industry_sector = Column(String(50), default="Finance")
    dataset_name = Column(String(100), nullable=False)
    local_sample_count = Column(Integer, default=1000)
    
    # Status
    status = Column(String(30), default="active")  # active, training, completed, offline
    current_round = Column(Integer, default=0)
    local_accuracy = Column(Float, nullable=True)
    local_loss = Column(Float, nullable=True)
    
    last_heartbeat = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class FederatedRound(Base):
    __tablename__ = "federated_rounds"

    id = Column(Integer, primary_key=True, index=True)
    round_number = Column(Integer, unique=True, index=True, nullable=False)
    status = Column(String(30), default="completed")  # in_progress, completed, failed
    aggregation_strategy = Column(String(50), default="FedAvg")
    
    # Participating clients & sample counts
    participating_clients = Column(JSON, default=list)  # list of client_ids
    total_samples = Column(Integer, default=0)
    
    # Performance Evaluation (Before vs After Aggregation)
    global_accuracy_before = Column(Float, nullable=True)
    global_accuracy_after = Column(Float, nullable=True)
    global_loss_before = Column(Float, nullable=True)
    global_loss_after = Column(Float, nullable=True)
    
    # Client-specific updates summary (weights delta norms, privacy checks)
    client_metrics = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
