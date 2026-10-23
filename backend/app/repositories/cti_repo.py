from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.repositories.base import BaseRepository
from app.models.cti import IOC, ThreatRelationship
from app.models.mitre import MitreTechnique

class IOCRepository(BaseRepository[IOC]):
    def __init__(self):
        super().__init__(IOC)

    def get_by_value(self, db: Session, value: str) -> Optional[IOC]:
        return db.query(IOC).filter(IOC.value == value).first()

    def filter_iocs(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        ioc_type: Optional[str] = None,
        verification_status: Optional[str] = None,
        severity: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[IOC]:
        query = db.query(IOC)
        if ioc_type:
            query = query.filter(IOC.ioc_type == ioc_type)
        if verification_status:
            query = query.filter(IOC.verification_status == verification_status)
        if severity:
            query = query.filter(IOC.severity == severity)
        if search:
            query = query.filter(IOC.value.like(f"%{search}%"))
        return query.order_by(desc(IOC.last_seen)).offset(skip).limit(limit).all()

    def count_filtered(
        self,
        db: Session,
        ioc_type: Optional[str] = None,
        verification_status: Optional[str] = None,
        severity: Optional[str] = None,
        search: Optional[str] = None
    ) -> int:
        query = db.query(IOC)
        if ioc_type:
            query = query.filter(IOC.ioc_type == ioc_type)
        if verification_status:
            query = query.filter(IOC.verification_status == verification_status)
        if severity:
            query = query.filter(IOC.severity == severity)
        if search:
            query = query.filter(IOC.value.like(f"%{search}%"))
        return query.count()


class ThreatRelationshipRepository(BaseRepository[ThreatRelationship]):
    def __init__(self):
        super().__init__(ThreatRelationship)

    def get_relationships_for_entity(self, db: Session, entity_ref: str) -> List[ThreatRelationship]:
        return db.query(ThreatRelationship).filter(
            (ThreatRelationship.source_ref == entity_ref) | (ThreatRelationship.target_ref == entity_ref)
        ).all()


class MitreRepository(BaseRepository[MitreTechnique]):
    def __init__(self):
        super().__init__(MitreTechnique)

    def get_by_technique_id(self, db: Session, technique_id: str) -> Optional[MitreTechnique]:
        return db.query(MitreTechnique).filter(MitreTechnique.technique_id == technique_id).first()

ioc_repo = IOCRepository()
threat_rel_repo = ThreatRelationshipRepository()
mitre_repo = MitreRepository()
