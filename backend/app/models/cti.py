import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON, ForeignKey
from app.core.database import Base

class IOC(Base):
    __tablename__ = "iocs"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(255), unique=True, index=True, nullable=False)
    ioc_type = Column(String(50), index=True, nullable=False)  # ipv4, ipv6, domain, url, sha256, md5, port
    
    # Status separation as required by specification
    observed_status = Column(String(50), default="observed")  # observed, suspicious, flagged
    enrichment_status = Column(String(50), default="pending")  # pending, enriched, failed, not_found
    verification_status = Column(String(50), default="unverified")  # unverified, confirmed_malicious, benign_whitelisted, suspicious
    
    severity = Column(String(20), default="Medium")  # Low, Medium, High, Critical
    confidence_score = Column(Float, default=0.5)  # 0.0 to 1.0
    threat_types = Column(JSON, default=list)  # ["c2", "scanner", "botnet", "malware_host"]
    
    # Provenance
    source = Column(String(100), default="Flow Inspection Engine")
    description = Column(Text, nullable=True)
    
    # Enrichment metadata from external feeds (VirusTotal, AbuseIPDB, etc.)
    enrichment_data = Column(JSON, default=dict)
    reputation_score = Column(Integer, nullable=True)  # 0 to 100
    last_enriched_at = Column(DateTime, nullable=True)
    
    # Timestamps
    first_seen = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Associations
    related_alert_count = Column(Integer, default=0)
    related_incident_count = Column(Integer, default=0)
    tags = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ThreatRelationship(Base):
    __tablename__ = "threat_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_ref = Column(String(100), index=True, nullable=False)  # e.g. ioc:192.168.1.105 or alert:ALT-2026-0001
    source_type = Column(String(50), nullable=False)  # ioc, alert, flow, incident, threat_actor
    
    relationship_type = Column(String(50), nullable=False)  # connects_to, communicates_with, drops, indicates, part_of_campaign
    
    target_ref = Column(String(100), index=True, nullable=False)  # e.g. ioc:45.33.32.156 or mitre:T1046
    target_type = Column(String(50), nullable=False)  # ioc, alert, mitre_technique, incident
    
    confidence = Column(Float, default=0.7)
    rationale = Column(Text, nullable=True)
    evidence = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
