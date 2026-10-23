import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class MitreTechniqueResponse(BaseModel):
    id: int
    technique_id: str
    name: str
    tactic: str
    description: Optional[str] = None
    attack_categories: List[str] = []
    mapping_rationale: Optional[str] = None
    detection_rule_summary: Optional[str] = None
    attck_version: str
    confidence_weight: float
    url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

