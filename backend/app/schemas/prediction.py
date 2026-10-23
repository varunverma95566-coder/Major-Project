import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict



class FlowFeatureInput(BaseModel):
    src_ip: Optional[str] = "192.168.1.100"
    dst_ip: Optional[str] = "10.0.0.5"
    src_port: Optional[int] = 49152
    dst_port: Optional[int] = 80
    protocol: Optional[str] = "TCP"
    flow_duration: Optional[float] = 120.5
    fwd_pkts: Optional[float] = 15.0
    bwd_pkts: Optional[float] = 12.0
    fwd_bytes: Optional[float] = 1500.0
    bwd_bytes: Optional[float] = 4200.0
    flow_rate: Optional[float] = 47.3
    packet_rate: Optional[float] = 0.22
    features: Optional[Dict[str, Any]] = None  # Raw dictionary of arbitrary dataset features
    ingestion_source: Optional[str] = "live_capture"
    is_simulated: Optional[bool] = False
    ground_truth_attack: Optional[str] = None
    dataset_source: Optional[str] = None

class FeatureImportanceItem(BaseModel):
    feature: str
    value: Any
    contribution: float
    direction: str  # "increases_risk", "decreases_risk", "neutral"

class PredictionResponse(BaseModel):
    id: int
    flow_id: str
    timestamp: datetime.datetime
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    is_malicious: bool
    predicted_class: str
    confidence: float
    class_probabilities: Dict[str, float] = {}
    risk_score: float
    severity: str
    inference_time_ms: float
    model_version: Optional[str] = None
    feature_importances: List[FeatureImportanceItem] = []
    human_explanation: Optional[str] = None
    model_evidence: Dict[str, Any] = {}
    llm_interpretation: Optional[str] = None
    alert_created: bool = False
    ingestion_source: str = "live_capture"
    is_anomaly: bool = False
    is_simulated: bool = False
    ground_truth_attack: Optional[str] = None
    dataset_source: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BatchPredictionRequest(BaseModel):
    flows: List[FlowFeatureInput]
    create_alerts: bool = True
    ingestion_source: Optional[str] = "batch_api"


class BigFlowCategoryItem(BaseModel):
    name: str
    group: str
    is_attack: bool
    is_supported: bool
    partition_file: str
    unsupported_reason: Optional[str] = None


class BigFlowCategoriesResponse(BaseModel):
    status: str
    total_categories: int
    active_model_name: Optional[str] = None
    model_supported_count: int
    unsupported_count: int
    categories: List[BigFlowCategoryItem]


class BigFlowReplayRequest(BaseModel):
    category: str = "DoS"
    batch_size: int = Field(5, ge=1, le=20)
    create_alerts: bool = True


class BigFlowReplayItem(BaseModel):
    flow_id: str
    timestamp: datetime.datetime
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    ground_truth_attack: str
    ground_truth_label: int
    is_ground_truth_malicious: bool
    predicted_class: str
    confidence: float
    is_malicious: bool
    model_version: str
    model_supported: bool
    is_correct_prediction: bool
    unsupported_warning: Optional[str] = None
    risk_score: float
    severity: str
    inference_time_ms: float
    feature_importances: List[FeatureImportanceItem] = []
    human_explanation: Optional[str] = None
    dataset_source: str
    alert_created: bool = False
    is_anomaly: bool = False
    ingestion_source: str = "dataset_replay"
    is_simulated: bool = False


class BigFlowReplayResponse(BaseModel):
    category_requested: str
    processed_count: int
    malicious_count: int
    benign_count: int
    accuracy_on_supported: Optional[float] = None
    items: List[BigFlowReplayItem]


class FlowFileUploadResponse(BaseModel):
    filename: str
    total_parsed: int
    processed_count: int
    malicious_count: int
    benign_count: int
    anomaly_count: int
    alerts_created: int
    adapter_applied: str
    model_version: str
    items: List[PredictionResponse]


class LiveIngestRequest(BaseModel):
    flows: List[FlowFeatureInput]
    sensor_id: Optional[str] = "SENSOR-EDGE-01"
    interface: Optional[str] = "eth0"
    create_alerts: bool = True


class LiveIngestResponse(BaseModel):
    status: str
    sensor_id: str
    interface: str
    ingested_count: int
    malicious_count: int
    benign_count: int
    anomaly_count: int
    items: List[PredictionResponse]


class LiveStatusResponse(BaseModel):
    status: str
    interface: str
    sensor_id: str
    mode: str
    active_model: Optional[str] = None
    total_live_flows_captured: int
    live_alerts_generated: int
    last_capture_time: Optional[datetime.datetime] = None


