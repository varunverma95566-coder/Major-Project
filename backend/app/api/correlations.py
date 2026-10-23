from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.cti import ThreatGraphResponse
from app.cti.correlation import correlation_engine

router = APIRouter(prefix="/correlations", tags=["Threat Correlation & Graph"])

@router.get("/graph", response_model=ThreatGraphResponse)
def get_correlation_graph(db: Session = Depends(get_db)):
    nodes, edges = correlation_engine.correlate_alerts(db)
    return ThreatGraphResponse(nodes=nodes, edges=edges)
