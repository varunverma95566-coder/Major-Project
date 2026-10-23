from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.ml_model import MLModel

class MLModelRepository(BaseRepository[MLModel]):
    def __init__(self):
        super().__init__(MLModel)

    def get_by_name(self, db: Session, name: str) -> Optional[MLModel]:
        return db.query(MLModel).filter(MLModel.name == name).first()

    def get_active_model(self, db: Session) -> Optional[MLModel]:
        return db.query(MLModel).filter(MLModel.is_active == True).first()

    def set_active_model(self, db: Session, model_id: int) -> Optional[MLModel]:
        db.query(MLModel).update({MLModel.is_active: False})
        model = self.get_by_id(db, model_id)
        if model:
            model.is_active = True
            db.commit()
            db.refresh(model)
        return model

model_repo = MLModelRepository()
