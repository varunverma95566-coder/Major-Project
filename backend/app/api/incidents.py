import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.incident import Incident
from app.models.alert import Alert
from app.schemas.incident import IncidentResponse, IncidentCreate, IncidentUpdate
from app.repositories.incident_repo import incident_repo
from app.api.deps import get_current_user

router = APIRouter(prefix="/incidents", tags=["Incident Management"])

@router.get("", response_model=List[IncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    incidents = incident_repo.get_all(db)
    results = []
    for inc in incidents:
        alert_cnt = db.query(Alert).filter(Alert.incident_id == inc.id).count()
        r = IncidentResponse.model_validate(inc)
        r.linked_alert_count = alert_cnt
        results.append(r)
    return results

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = incident_repo.get_by_id(db, incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    alert_cnt = db.query(Alert).filter(Alert.incident_id == inc.id).count()
    res = IncidentResponse.model_validate(inc)
    res.linked_alert_count = alert_cnt
    return res

@router.post("", response_model=IncidentResponse)
def create_incident(
    data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    inc_code = f"INC-2026-{db.query(Incident).count() + 1:03d}"
    inc = Incident(
        incident_code=inc_code,
        title=data.title,
        description=data.description,
        severity=data.severity,
        status="Open",
        lead_analyst=data.lead_analyst or (current_user.username if current_user else "analyst"),
        affected_assets=data.affected_assets,
        associated_iocs=data.associated_iocs,
        mitre_techniques=data.mitre_techniques,
        timeline=[{
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "event": "Incident created from correlation trigger",
            "user": current_user.username if current_user else "analyst"
        }]
    )
    db.add(inc)
    db.commit()
    db.refresh(inc)

    # Link alerts
    if data.alert_ids:
        for aid in data.alert_ids:
            alert = db.query(Alert).filter(Alert.id == aid).first()
            if alert:
                alert.incident_id = inc.id
        db.commit()

    alert_cnt = len(data.alert_ids or [])
    res = IncidentResponse.model_validate(inc)
    res.linked_alert_count = alert_cnt
    return res

@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    inc = incident_repo.get_by_id(db, incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    if data.title:
        inc.title = data.title
    if data.description:
        inc.description = data.description
    if data.severity:
        inc.severity = data.severity
    if data.status:
        inc.status = data.status
        if data.status in ["Resolved", "Closed"]:
            inc.resolved_at = datetime.datetime.utcnow()
    if data.lead_analyst:
        inc.lead_analyst = data.lead_analyst
    if data.root_cause:
        inc.root_cause = data.root_cause
    if data.mitigation_steps:
        inc.mitigation_steps = data.mitigation_steps

    if data.new_timeline_event:
        tl = list(inc.timeline or [])
        tl.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "event": data.new_timeline_event,
            "user": current_user.username if current_user else "analyst"
        })
        inc.timeline = tl

    inc.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(inc)
    
    alert_cnt = db.query(Alert).filter(Alert.incident_id == inc.id).count()
    res = IncidentResponse.model_validate(inc)
    res.linked_alert_count = alert_cnt
    return res
