import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class FederatedClientResponse(BaseModel):
    id: int
    client_id: str
    name: str
    organization: str
    industry_sector: str
    dataset_name: str
    local_sample_count: int
    status: str
    current_round: int
    local_accuracy: Optional[float] = None
    local_loss: Optional[float] = None
    last_heartbeat: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class TriggerRoundRequest(BaseModel):
    client_ids: Optional[List[str]] = None
    local_epochs: int = 2
    aggregation_strategy: str = "FedAvg"

class FederatedRoundResponse(BaseModel):
    id: int
    round_number: int
    status: str
    aggregation_strategy: str
    participating_clients: List[str]
    total_samples: int
    global_accuracy_before: Optional[float] = None
    global_accuracy_after: Optional[float] = None
    global_loss_before: Optional[float] = None
    global_loss_after: Optional[float] = None
    client_metrics: Dict[str, Any] = {}
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)

