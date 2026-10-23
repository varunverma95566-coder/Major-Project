from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.repositories.base import BaseRepository
from app.models.federated import FederatedClient, FederatedRound

class FederatedClientRepository(BaseRepository[FederatedClient]):
    def __init__(self):
        super().__init__(FederatedClient)

    def get_by_client_id(self, db: Session, client_id: str) -> Optional[FederatedClient]:
        return db.query(FederatedClient).filter(FederatedClient.client_id == client_id).first()


class FederatedRoundRepository(BaseRepository[FederatedRound]):
    def __init__(self):
        super().__init__(FederatedRound)

    def get_latest_round(self, db: Session) -> Optional[FederatedRound]:
        return db.query(FederatedRound).order_by(desc(FederatedRound.round_number)).first()

    def get_history(self, db: Session, limit: int = 20) -> List[FederatedRound]:
        return db.query(FederatedRound).order_by(desc(FederatedRound.round_number)).limit(limit).all()

federated_client_repo = FederatedClientRepository()
federated_round_repo = FederatedRoundRepository()
