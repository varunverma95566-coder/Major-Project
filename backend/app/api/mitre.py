from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.mitre import MitreTechnique
from app.schemas.mitre import MitreTechniqueResponse
from app.repositories.cti_repo import mitre_repo

router = APIRouter(prefix="/mitre", tags=["MITRE ATT&CK Mapping"])

@router.get("/techniques", response_model=List[MitreTechniqueResponse])
def list_mitre_techniques(db: Session = Depends(get_db)):
    return mitre_repo.get_all(db)
