import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict



class ArchitectureConfig(BaseModel):
    embedding_dim: int = Field(64, description="Feature projection dimension (must be divisible by num_heads)")
    num_heads: int = Field(4, description="Number of multi-head attention heads")
    num_layers: int = Field(2, description="Number of Transformer encoder layers")
    dropout: float = Field(0.1, description="Dropout rate")
    feedforward_dim: int = Field(128, description="Feedforward hidden layer dimension")

class TrainModelRequest(BaseModel):
    name: str = Field(..., description="Unique model name/version tag")
    dataset_id: int = Field(..., description="ID of validated dataset to train on")
    description: Optional[str] = "FlowTransformer classifier trained on network flows"
    epochs: int = Field(5, ge=1, le=50)
    batch_size: int = Field(64, ge=8, le=512)
    learning_rate: float = Field(0.001, gt=0, le=0.1)
    train_baseline: bool = Field(True, description="Also train Random Forest baseline for empirical comparison")
    architecture: ArchitectureConfig = Field(default_factory=ArchitectureConfig)

class EvaluationMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float] = None
    per_class_metrics: Dict[str, Dict[str, float]] = {}
    confusion_matrix: List[List[int]] = []
    classes: List[str] = []

class MLModelResponse(BaseModel):
    id: int
    name: str
    version: str
    model_type: str
    description: Optional[str] = None
    dataset_id: Optional[int] = None
    architecture_config: Dict[str, Any] = {}
    target_classes: List[str] = []
    status: str
    is_active: bool
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc: Optional[float] = None
    per_class_metrics: Optional[Dict[str, Any]] = None
    confusion_matrix: Optional[List[List[int]]] = None
    training_history: Optional[Dict[str, Any]] = None
    baseline_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)


