import datetime
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, ConfigDict


class ColumnInfo(BaseModel):
    name: str
    dtype: str
    missing_count: int
    is_numeric: bool
    sample_values: List[Any] = []

class DatasetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    adapter_type: str
    file_path: str
    file_size_bytes: int
    total_rows: int
    total_columns: int
    benign_count: int
    malicious_count: int
    column_info: Optional[Union[List[Any], Dict[str, Any]]] = None
    class_distribution: Dict[str, int] = {}
    is_validated: bool
    is_sample: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetAnalysisResult(BaseModel):
    dataset_id: int
    name: str
    total_rows: int
    total_columns: int
    benign_count: int
    malicious_count: int
    class_distribution: Dict[str, int]
    detected_adapter: str
    detected_features: List[str]
    missing_values_summary: Dict[str, int]
