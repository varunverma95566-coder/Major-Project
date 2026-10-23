import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_code = Column(String(50), unique=True, index=True, nullable=False)  # e.g. ALT-2026-0001
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Classification & Severity
    category = Column(String(50), index=True, nullable=False)  # DoS, PortScan, BruteForce, Malware, etc.
    severity = Column(String(20), index=True, default="Medium")  # Informational, Low, Medium, High, Critical
    risk_score = Column(Float, index=True, default=50.0)  # 0 to 100
    confidence = Column(Float, default=0.85)
    
    # Network context
    src_ip = Column(String(50), index=True, nullable=True)
    dst_ip = Column(String(50), index=True, nullable=True)
    src_port = Column(Integer, nullable=True)
    dst_port = Column(Integer, nullable=True)
    protocol = Column(String(20), nullable=True)
    
    # Association
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    mitre_technique_id = Column(String(20), nullable=True)
    
    # Lifecycle
    status = Column(String(30), index=True, default="New")  # New, Acknowledged, Investigating, Resolved, False Positive
    assigned_to = Column(String(100), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Supporting evidence
    evidence = Column(JSON, default=dict)
    investigation_notes = Column(JSON, default=list)  # list of {timestamp, author, note}
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
