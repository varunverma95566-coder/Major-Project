import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class AlertNote(BaseModel):
    timestamp: str
    author: str
    note: str

class AlertCreate(BaseModel):
    title: str
    category: str
    severity: str = "Medium"
    risk_score: float = 50.0
    confidence: float = 0.85
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    prediction_id: Optional[int] = None
    mitre_technique_id: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

class AlertUpdate(BaseModel):
    status: Optional[str] = None  # New, Acknowledged, Investigating, Resolved, False Positive
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    incident_id: Optional[int] = None
    new_note: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    alert_code: str
    title: str
    description: Optional[str] = None
    category: str
    severity: str
    risk_score: float
    confidence: float
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    prediction_id: Optional[int] = None
    incident_id: Optional[int] = None
    mitre_technique_id: Optional[str] = None
    status: str
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    evidence: Dict[str, Any] = {}
    investigation_notes: List[Dict[str, Any]] = []
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

