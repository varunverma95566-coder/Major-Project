from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.repositories.base import BaseRepository
from app.models.alert import Alert

class AlertRepository(BaseRepository[Alert]):
    def __init__(self):
        super().__init__(Alert)

    def get_by_code(self, db: Session, alert_code: str) -> Optional[Alert]:
        return db.query(Alert).filter(Alert.alert_code == alert_code).first()

    def get_recent(self, db: Session, limit: int = 10) -> List[Alert]:
        return db.query(Alert).order_by(desc(Alert.created_at)).limit(limit).all()

    def filter_alerts(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Alert]:
        query = db.query(Alert)
        if status:
            query = query.filter(Alert.status == status)
        if severity:
            query = query.filter(Alert.severity == severity)
        if category:
            query = query.filter(Alert.category == category)
        return query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()

    def count_filtered(
        self,
        db: Session,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None
    ) -> int:
        query = db.query(Alert)
        if status:
            query = query.filter(Alert.status == status)
        if severity:
            query = query.filter(Alert.severity == severity)
        if category:
            query = query.filter(Alert.category == category)
        return query.count()

alert_repo = AlertRepository()
