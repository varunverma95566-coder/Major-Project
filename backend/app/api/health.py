import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.schemas.common import HealthResponse
from app.repositories.model_repo import model_repo

router = APIRouter(prefix="/health", tags=["System Health"])

@router.get("", response_model=HealthResponse)
def get_system_health(db: Session = Depends(get_db)):
    active_m = model_repo.get_active_model(db)
    return HealthResponse(
        status="healthy",
        environment=settings.ENVIRONMENT,
        version=settings.PROJECT_VERSION,
        database="SQLite (Development Mode)" if "sqlite" in settings.DATABASE_URL else "Production Database",
        active_model=active_m.name if active_m else "None",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

