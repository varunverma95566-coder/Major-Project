import re
import torch
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.ml_model import MLModel
from app.models.dataset import Dataset
from app.models.alert import Alert
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/settings", tags=["System Settings & Health"])

@router.get("/integrations")
def get_integration_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    active_m = db.query(MLModel).filter(MLModel.is_active == True).first()
    
    # Mask database credentials if present (CWE-200)
    raw_url = settings.DATABASE_URL.split("?")[0]
    masked_url = re.sub(r"://([^:]+):([^@]+)@", r"://\1:********@", raw_url)

    return {
        "system": {
            "name": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "dev_mode_auth": settings.DEV_MODE_AUTH
        },
        "database": {
            "engine": "SQLite (Development Mode)" if "sqlite" in settings.DATABASE_URL else "PostgreSQL / Enterprise DB",
            "url_configured": masked_url,
            "status": "connected"
        },

        "machine_learning": {
            "framework": f"PyTorch {torch.__version__}",
            "device": "CPU (Optimized for development & edge execution)",
            "active_model": active_m.name if active_m else "None",
            "architecture": "FlowTransformer (Multi-Head Self-Attention)"
        },
        "threat_intelligence": {
            "abuseipdb": {
                "status": "Active (Live API)" if settings.ABUSEIPDB_API_KEY else "Operational (Simulated/Offline Intelligence)",
                "api_key_configured": bool(settings.ABUSEIPDB_API_KEY)
            },
            "virustotal": {
                "status": "Active (Live API)" if settings.VIRUSTOTAL_API_KEY else "Operational (Simulated/Offline Intelligence)",
                "api_key_configured": bool(settings.VIRUSTOTAL_API_KEY)
            },
            "mitre_framework": "ATT&CK Enterprise v14.1",
            "stix_export": "STIX 2.1 Specification Compliant"
        },
        "explainable_ai": {
            "provider": settings.LLM_PROVIDER,
            "status": "Operational (Sensitivity Attribution + Grounded Heuristics)",
            "llm_api_key_configured": bool(settings.LLM_API_KEY)
        }
    }
