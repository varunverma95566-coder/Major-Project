from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.repositories.base import BaseRepository
from app.models.audit import AuditEvent, SystemSetting

class AuditRepository(BaseRepository[AuditEvent]):
    def __init__(self):
        super().__init__(AuditEvent)

    def log_event(
        self,
        db: Session,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        username: str = "system",
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditEvent:
        event = AuditEvent(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            username=username,
            status=status,
            details=details or {},
            ip_address=ip_address
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def get_recent(self, db: Session, limit: int = 50) -> List[AuditEvent]:
        return db.query(AuditEvent).order_by(desc(AuditEvent.timestamp)).limit(limit).all()


class SettingsRepository(BaseRepository[SystemSetting]):
    def __init__(self):
        super().__init__(SystemSetting)

    def get_by_key(self, db: Session, key: str) -> Optional[SystemSetting]:
        return db.query(SystemSetting).filter(SystemSetting.key == key).first()

audit_repo = AuditRepository()
settings_repo = SettingsRepository()
