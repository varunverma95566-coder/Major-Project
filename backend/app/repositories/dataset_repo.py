from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.dataset import Dataset

class DatasetRepository(BaseRepository[Dataset]):
    def __init__(self):
        super().__init__(Dataset)

    def get_by_name(self, db: Session, name: str) -> Optional[Dataset]:
        return db.query(Dataset).filter(Dataset.name == name).first()

    def get_samples(self, db: Session) -> List[Dataset]:
        return db.query(Dataset).filter(Dataset.is_sample == True).all()

dataset_repo = DatasetRepository()
