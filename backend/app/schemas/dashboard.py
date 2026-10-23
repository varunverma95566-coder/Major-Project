from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.schemas.alert import AlertResponse
from app.schemas.ml import MLModelResponse

class TimeSeriesPoint(BaseModel):
    timestamp: str
    total_flows: int
    malicious_flows: int
    benign_flows: int

class DashboardMetricsResponse(BaseModel):
    total_analyzed_flows: int
    benign_flows: int
    malicious_flows: int
    detection_rate_pct: float
    false_positive_rate_pct: float
    total_alerts: int
    critical_alerts: int
    open_incidents: int
    total_iocs: int
    active_model_name: Optional[str] = None
    active_model_accuracy: Optional[float] = None
    
    attack_class_distribution: Dict[str, int] = {}
    alert_severity_distribution: Dict[str, int] = {}
    top_source_ips: List[Dict[str, Any]] = []
    top_dest_ports: List[Dict[str, Any]] = []
    detection_activity_timeline: List[TimeSeriesPoint] = []
    
    recent_alerts: List[AlertResponse] = []
    recent_models: List[MLModelResponse] = []
    federated_status: Dict[str, Any] = {}
    cti_summary: Dict[str, Any] = {}
    anomaly_flows: int = 0
    by_ingestion_source: Dict[str, int] = {}

