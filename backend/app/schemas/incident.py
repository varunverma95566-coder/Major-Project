import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "Medium"
    lead_analyst: Optional[str] = None
    affected_assets: List[str] = []
    associated_iocs: List[str] = []
    mitre_techniques: List[str] = []
    alert_ids: Optional[List[int]] = None

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None  # Open, In Progress, Contained, Resolved, Closed
    lead_analyst: Optional[str] = None
    root_cause: Optional[str] = None
    mitigation_steps: Optional[str] = None
    new_timeline_event: Optional[str] = None

class IncidentResponse(BaseModel):
    id: int
    incident_code: str
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    lead_analyst: Optional[str] = None
    affected_assets: List[str] = []
    associated_iocs: List[str] = []
    mitre_tactics: List[str] = []
    mitre_techniques: List[str] = []
    root_cause: Optional[str] = None
    mitigation_steps: Optional[str] = None
    timeline: List[Dict[str, Any]] = []
    linked_alert_count: int = 0
    created_at: datetime.datetime
    updated_at: datetime.datetime
    resolved_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)

