import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON, ForeignKey
from app.core.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Contextual Flow Metadata
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    src_ip = Column(String(50), index=True, nullable=True)
    dst_ip = Column(String(50), index=True, nullable=True)
    src_port = Column(Integer, nullable=True)
    dst_port = Column(Integer, index=True, nullable=True)
    protocol = Column(String(20), nullable=True)
    
    # Raw / Normalized Flow Features snapshot
    flow_features = Column(JSON, default=dict)
    
    # Model inference results
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=True)
    model_version = Column(String(50), nullable=True)
    is_malicious = Column(Boolean, index=True, nullable=False)
    predicted_class = Column(String(50), index=True, nullable=False)
    confidence = Column(Float, nullable=False)
    class_probabilities = Column(JSON, default=dict)
    inference_time_ms = Column(Float, default=0.0)
    
    # Risk Assessment
    risk_score = Column(Float, index=True, default=0.0)  # 0 to 100
    severity = Column(String(20), index=True, default="Low")  # Informational, Low, Medium, High, Critical
    
    # Explainable AI Results (eX-NIDS)
    feature_importances = Column(JSON, default=list)  # [{feature, value, contribution, direction}]
    human_explanation = Column(Text, nullable=True)
    model_evidence = Column(JSON, default=dict)
    llm_interpretation = Column(Text, nullable=True)
    
    # Status & Provenance
    alert_created = Column(Boolean, default=False)
    ingestion_source = Column(String(50), default="live_capture", index=True)  # live_capture, dataset_replay, file_upload, simulated_preset
    is_anomaly = Column(Boolean, default=False, index=True)
    is_simulated = Column(Boolean, default=False, index=True)
    ground_truth_attack = Column(String(100), nullable=True)
    dataset_source = Column(String(150), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
