import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_code = Column(String(50), unique=True, index=True, nullable=False)  # e.g. INC-2026-001
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    severity = Column(String(20), index=True, default="Medium")  # Low, Medium, High, Critical
    status = Column(String(30), index=True, default="Open")  # Open, In Progress, Contained, Resolved, Closed
    lead_analyst = Column(String(100), nullable=True)
    
    # Scope and Impact
    affected_assets = Column(JSON, default=list)  # list of IP addresses or hostnames
    associated_iocs = Column(JSON, default=list)
    mitre_tactics = Column(JSON, default=list)
    mitre_techniques = Column(JSON, default=list)
    
    # Analysis & Resolution
    root_cause = Column(Text, nullable=True)
    mitigation_steps = Column(Text, nullable=True)
    timeline = Column(JSON, default=list)  # list of {timestamp, event, user}
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
