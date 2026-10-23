import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    version = Column(String(50), nullable=False)
    model_type = Column(String(50), default="FlowTransformer")  # FlowTransformer, RandomForestBaseline
    description = Column(Text, nullable=True)
    
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=True)
    
    # Model Architecture Config
    architecture_config = Column(JSON, default=dict)  # {embedding_dim, num_heads, num_layers, dropout, etc.}
    
    # Preprocessor and Artifact storage paths
    weights_path = Column(String(255), nullable=True)
    preprocessor_path = Column(String(255), nullable=True)
    
    # Target classes mapping
    target_classes = Column(JSON, default=list)  # ["Benign", "DoS", "PortScan", ...]
    binary_threshold = Column(Float, default=0.5)
    
    # Status
    status = Column(String(30), default="untrained")  # untrained, training, trained, failed
    is_active = Column(Boolean, default=False)  # Current active model for inference
    
    # Evaluation Metrics on Held-out test set
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    per_class_metrics = Column(JSON, default=dict)
    confusion_matrix = Column(JSON, default=list)
    training_history = Column(JSON, default=dict)  # train_loss, val_loss, train_acc, val_acc per epoch
    
    # Baseline comparison metrics
    baseline_metrics = Column(JSON, default=dict)  # Random Forest baseline metrics for comparison
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
