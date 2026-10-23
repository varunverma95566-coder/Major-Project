"""Main FastAPI Application Entrypoint.

Transformer-Based Network Intrusion Detection & Cyber Threat Intelligence Platform.
Mounts all REST API endpoints, initializes database sessions, CORS, and active ML models.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import SessionLocal, Base, engine
from app.ml.inference import inference_service
from app.repositories.model_repo import model_repo

# Import API routers
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.datasets import router as datasets_router
from app.api.models import router as models_router
from app.api.predictions import router as predictions_router
from app.api.alerts import router as alerts_router
from app.api.incidents import router as incidents_router
from app.api.iocs import router as iocs_router
from app.api.cti import router as cti_router
from app.api.correlations import router as correlations_router
from app.api.mitre import router as mitre_router
from app.api.federated import router as federated_router
from app.api.reports import router as reports_router
from app.api.settings import router as settings_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist & attempt to load active model
    Base.metadata.create_all(bind=engine)
    # Safe SQLite column migrations for new provenance and anomaly tracking fields
    from sqlalchemy import text
    with engine.connect() as conn:
        for col, col_type in [
            ("ingestion_source", "VARCHAR(50) DEFAULT 'live_capture'"),
            ("is_anomaly", "BOOLEAN DEFAULT 0"),
            ("is_simulated", "BOOLEAN DEFAULT 0"),
            ("ground_truth_attack", "VARCHAR(100)"),
            ("dataset_source", "VARCHAR(150)")
        ]:
            try:
                conn.execute(text(f"ALTER TABLE predictions ADD COLUMN {col} {col_type}"))
                conn.commit()
            except Exception:
                pass
    logger.info("Database schemas verified.")
    
    db = SessionLocal()
    try:
        active_m = model_repo.get_active_model(db)
        if active_m:
            loaded = inference_service.load_model(active_m.name)
            if loaded:
                logger.info(f"Loaded active FlowTransformer model '{active_m.name}'.")
    except Exception as e:
        logger.warning(f"Could not load active model on startup: {e}")
    finally:
        db.close()
        
    yield
    logger.info("Application shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Production-ready Transformer-Based NIDS and Cyber Threat Intelligence Platform API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"https://.*(\.github\.io|\.trycloudflare\.com|\.onrender\.com|\.railway\.app)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routers
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(datasets_router, prefix=settings.API_PREFIX)
app.include_router(models_router, prefix=settings.API_PREFIX)
app.include_router(predictions_router, prefix=settings.API_PREFIX)
app.include_router(alerts_router, prefix=settings.API_PREFIX)
app.include_router(incidents_router, prefix=settings.API_PREFIX)
app.include_router(iocs_router, prefix=settings.API_PREFIX)
app.include_router(cti_router, prefix=settings.API_PREFIX)
app.include_router(correlations_router, prefix=settings.API_PREFIX)
app.include_router(mitre_router, prefix=settings.API_PREFIX)
app.include_router(federated_router, prefix=settings.API_PREFIX)
app.include_router(reports_router, prefix=settings.API_PREFIX)
app.include_router(settings_router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
