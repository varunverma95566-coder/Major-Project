from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.federated import FederatedClient, FederatedRound
from app.models.user import User
from app.schemas.federated import FederatedClientResponse, FederatedRoundResponse, TriggerRoundRequest
from app.repositories.federated_repo import federated_client_repo, federated_round_repo
from app.federated.simulation import run_federated_round
from app.api.deps import require_analyst_or_admin

router = APIRouter(prefix="/federated", tags=["Federated Learning Simulation"])

@router.get("/clients", response_model=List[FederatedClientResponse])
def list_federated_clients(db: Session = Depends(get_db)):
    return federated_client_repo.get_all(db)

@router.get("/rounds", response_model=List[FederatedRoundResponse])
def list_federated_rounds(db: Session = Depends(get_db)):
    return federated_round_repo.get_history(db)

@router.post("/rounds/trigger", response_model=FederatedRoundResponse)
def trigger_federated_round(
    request: TriggerRoundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)
):
    try:
        res = run_federated_round(
            db,
            base_model_name="flow_transformer_v1",
            client_ids=request.client_ids,
            local_epochs=request.local_epochs
        )
        latest = federated_round_repo.get_latest_round(db)
        return latest
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

