import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON
from app.core.database import Base

class MitreTechnique(Base):
    __tablename__ = "mitre_techniques"

    id = Column(Integer, primary_key=True, index=True)
    technique_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g. T1046
    name = Column(String(150), nullable=False)
    tactic = Column(String(100), index=True, nullable=False)  # e.g. Discovery, Impact, Execution
    description = Column(Text, nullable=True)
    
    # Associated detection logic
    attack_categories = Column(JSON, default=list)  # ["PortScan", "Reconnaissance"]
    mapping_rationale = Column(Text, nullable=True)
    detection_rule_summary = Column(Text, nullable=True)
    
    # Versioning & Metadata
    attck_version = Column(String(20), default="v14.1")
    confidence_weight = Column(Float, default=0.85)
    url = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
