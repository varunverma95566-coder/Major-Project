import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.cti import IOC
from app.schemas.cti import IOCResponse, IOCCreate, IOCUpdate
from app.schemas.common import PaginatedResponse
from app.repositories.cti_repo import ioc_repo
from app.cti.enrichment import enrichment_service

router = APIRouter(prefix="/iocs", tags=["IOC & Threat Context Management"])

@router.get("", response_model=PaginatedResponse[IOCResponse])
def list_iocs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    ioc_type: Optional[str] = None,
    verification_status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    items = ioc_repo.filter_iocs(
        db, skip=skip, limit=page_size,
        ioc_type=ioc_type,
        verification_status=verification_status,
        severity=severity,
        search=search
    )
    total = ioc_repo.count_filtered(
        db,
        ioc_type=ioc_type,
        verification_status=verification_status,
        severity=severity,
        search=search
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse(
        items=[IOCResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{ioc_id}", response_model=IOCResponse)
def get_ioc(ioc_id: int, db: Session = Depends(get_db)):
    i = ioc_repo.get_by_id(db, ioc_id)
    if not i:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return i

@router.post("", response_model=IOCResponse)
def create_ioc(data: IOCCreate, db: Session = Depends(get_db)):
    existing = ioc_repo.get_by_value(db, data.value)
    if existing:
        return existing

    # Auto-enrich IP upon creation
    enrich_data = {}
    reputation = None
    if data.ioc_type == "ipv4":
        enrich_data = enrichment_service.enrich_ip(data.value)
        reputation = enrich_data.get("reputation_score")

    ioc_obj = ioc_repo.create(db, {
        "value": data.value,
        "ioc_type": data.ioc_type,
        "observed_status": data.observed_status,
        "enrichment_status": "enriched" if enrich_data else "pending",
        "verification_status": data.verification_status,
        "severity": data.severity,
        "confidence_score": data.confidence_score,
        "threat_types": enrich_data.get("threat_types", []),
        "source": data.source,
        "description": data.description,
        "enrichment_data": enrich_data,
        "reputation_score": reputation,
        "last_enriched_at": datetime.datetime.utcnow() if enrich_data else None,
        "tags": data.tags
    })
    return ioc_obj

@router.patch("/{ioc_id}", response_model=IOCResponse)
def update_ioc(ioc_id: int, update: IOCUpdate, db: Session = Depends(get_db)):
    ioc = ioc_repo.get_by_id(db, ioc_id)
    if not ioc:
        raise HTTPException(status_code=404, detail="Indicator not found")

    if update.verification_status:
        ioc.verification_status = update.verification_status
    if update.observed_status:
        ioc.observed_status = update.observed_status
    if update.severity:
        ioc.severity = update.severity
    if update.confidence_score is not None:
        ioc.confidence_score = update.confidence_score
    if update.description:
        ioc.description = update.description
    if update.tags:
        ioc.tags = update.tags

    ioc.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(ioc)
    return ioc
