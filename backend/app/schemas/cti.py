import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class IOCCreate(BaseModel):
    value: str
    ioc_type: str  # ipv4, ipv6, domain, url, sha256, port
    observed_status: str = "observed"
    verification_status: str = "unverified"
    severity: str = "Medium"
    confidence_score: float = 0.5
    source: str = "Manual Entry"
    description: Optional[str] = None
    tags: List[str] = []

class IOCUpdate(BaseModel):
    observed_status: Optional[str] = None
    enrichment_status: Optional[str] = None
    verification_status: Optional[str] = None
    severity: Optional[str] = None
    confidence_score: Optional[float] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class IOCResponse(BaseModel):
    id: int
    value: str
    ioc_type: str
    observed_status: str
    enrichment_status: str
    verification_status: str
    severity: str
    confidence_score: float
    threat_types: List[str] = []
    source: str
    description: Optional[str] = None
    enrichment_data: Dict[str, Any] = {}
    reputation_score: Optional[int] = None
    last_enriched_at: Optional[datetime.datetime] = None
    first_seen: datetime.datetime
    last_seen: datetime.datetime
    related_alert_count: int = 0
    tags: List[str] = []
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # ioc, alert, incident, mitre
    severity: Optional[str] = None
    details: Dict[str, Any] = {}

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship: str
    confidence: float

class ThreatGraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class STIXExportResponse(BaseModel):
    spec_version: str = "2.1"
    id: str
    type: str = "bundle"
    objects: List[Dict[str, Any]]
