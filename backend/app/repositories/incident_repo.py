from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.repositories.base import BaseRepository
from app.models.incident import Incident
from app.models.alert import Alert

class IncidentRepository(BaseRepository[Incident]):
    def __init__(self):
        super().__init__(Incident)

    def get_by_code(self, db: Session, incident_code: str) -> Optional[Incident]:
        return db.query(Incident).filter(Incident.incident_code == incident_code).first()

    def get_open_incidents(self, db: Session) -> List[Incident]:
        return db.query(Incident).filter(Incident.status.in_(["Open", "In Progress"])).order_by(desc(Incident.created_at)).all()

    def get_linked_alerts(self, db: Session, incident_id: int) -> List[Alert]:
        return db.query(Alert).filter(Alert.incident_id == incident_id).all()

incident_repo = IncidentRepository()
