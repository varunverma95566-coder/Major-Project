import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON
from app.core.database import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    username = Column(String(50), index=True, default="system")
    action = Column(String(50), index=True, nullable=False)  # login, alert_status_change, model_trained, incident_created, export_stix, etc.
    resource_type = Column(String(50), index=True, nullable=False)  # alert, incident, model, dataset, cti, system
    resource_id = Column(String(100), nullable=True)
    status = Column(String(20), default="success")  # success, failure, denied
    details = Column(JSON, default=dict)
    ip_address = Column(String(50), nullable=True)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    is_secret = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
