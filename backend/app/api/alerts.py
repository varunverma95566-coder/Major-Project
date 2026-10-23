import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.alert import Alert
from app.models.incident import Incident
from app.schemas.alert import AlertResponse, AlertCreate, AlertUpdate
from app.schemas.common import PaginatedResponse
from app.repositories.alert_repo import alert_repo
from app.api.deps import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alert Management"])

@router.get("", response_model=PaginatedResponse[AlertResponse])
def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    items = alert_repo.filter_alerts(db, skip=skip, limit=page_size, status=status, severity=severity, category=category)
    total = alert_repo.count_filtered(db, status=status, severity=severity, category=category)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse(
        items=[AlertResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    a = alert_repo.get_by_id(db, alert_id)
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    return a

@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    update_data: AlertUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    alert = alert_repo.get_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if update_data.status:
        alert.status = update_data.status
    if update_data.assigned_to:
        alert.assigned_to = update_data.assigned_to
    if update_data.resolution_notes:
        alert.resolution_notes = update_data.resolution_notes
    if update_data.incident_id:
        alert.incident_id = update_data.incident_id

    if update_data.new_note:
        notes = list(alert.investigation_notes or [])
        notes.append({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "author": current_user.username if current_user else "analyst",
            "note": update_data.new_note
        })
        alert.investigation_notes = notes

    alert.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert

