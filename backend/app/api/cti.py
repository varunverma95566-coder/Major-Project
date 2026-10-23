import io
import re
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import pandas as pd
from app.core.database import get_db
from app.models.cti import IOC
from app.models.alert import Alert
from app.schemas.cti import STIXExportResponse
from app.cti.enrichment import enrichment_service
from app.cti.stix_export import export_iocs_to_stix


def sanitize_csv_cell(value: Any) -> Any:
    """Neutralizes formula injection characters (=, +, -, @, tab, CR) for spreadsheet safety (CWE-1236)."""
    if isinstance(value, str):
        # If the string starts with a formula trigger character, prepend a single quote
        if value and value[0] in ("=", "+", "-", "@", "\t", "\r"):
            return f"'{value}"
    return value


router = APIRouter(prefix="/cti", tags=["Cyber Threat Intelligence & Sharing"])

@router.post("/enrich")
def enrich_indicator(target: str = Query(..., description="IP or indicator value"), db: Session = Depends(get_db)):
    clean_target = target.strip()
    if not clean_target or len(clean_target) > 255:
        raise HTTPException(status_code=400, detail="Invalid indicator target provided.")

    enrich_data = enrichment_service.enrich_ip(clean_target)
    
    # Update indicator in DB if exists
    ioc = db.query(IOC).filter(IOC.value == clean_target).first()
    if ioc:
        ioc.enrichment_data = enrich_data
        ioc.reputation_score = enrich_data.get("reputation_score")
        ioc.enrichment_status = "enriched"
        if enrich_data.get("verification_status"):
            ioc.verification_status = enrich_data["verification_status"]
        if enrich_data.get("threat_types"):
            ioc.threat_types = enrich_data["threat_types"]
        db.commit()
        db.refresh(ioc)

    return {"target": clean_target, "enrichment": enrich_data}

@router.get("/export/stix", response_model=STIXExportResponse)
def export_stix_bundle(db: Session = Depends(get_db)):
    iocs = db.query(IOC).all()
    alerts = db.query(Alert).limit(20).all()
    bundle = export_iocs_to_stix(iocs, alerts)
    return bundle

@router.get("/export/csv")
def export_iocs_csv(db: Session = Depends(get_db)):
    iocs = db.query(IOC).all()
    rows = []
    for i in iocs:
        rows.append({
            "Indicator": sanitize_csv_cell(i.value),
            "Type": sanitize_csv_cell(i.ioc_type),
            "Observed_Status": sanitize_csv_cell(i.observed_status),
            "Verification_Status": sanitize_csv_cell(i.verification_status),
            "Severity": sanitize_csv_cell(i.severity),
            "Reputation_Score": i.reputation_score if i.reputation_score is not None else 0,
            "Confidence": round(float(i.confidence_score or 0.0), 2),
            "Threat_Types": sanitize_csv_cell(",".join(i.threat_types or [])),
            "First_Seen": i.first_seen.isoformat() if i.first_seen else "",
            "Last_Seen": i.last_seen.isoformat() if i.last_seen else ""
        })
    df = pd.DataFrame(rows)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    response = Response(content=stream.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=nids_cti_iocs_export.csv"
    return response

