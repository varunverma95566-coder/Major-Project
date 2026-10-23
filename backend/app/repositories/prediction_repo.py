from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.repositories.base import BaseRepository
from app.models.prediction import Prediction

class PredictionRepository(BaseRepository[Prediction]):
    def __init__(self):
        super().__init__(Prediction)

    def get_recent(self, db: Session, limit: int = 50) -> List[Prediction]:
        return db.query(Prediction).order_by(desc(Prediction.timestamp)).limit(limit).all()

    def filter_flows(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        is_malicious: Optional[bool] = None,
        predicted_class: Optional[str] = None,
        severity: Optional[str] = None,
        src_ip: Optional[str] = None,
        ingestion_source: Optional[str] = None,
        is_anomaly: Optional[bool] = None
    ) -> List[Prediction]:
        query = db.query(Prediction)
        if is_malicious is not None:
            query = query.filter(Prediction.is_malicious == is_malicious)
        if predicted_class:
            query = query.filter(Prediction.predicted_class == predicted_class)
        if severity:
            query = query.filter(Prediction.severity == severity)
        if src_ip:
            query = query.filter(Prediction.src_ip.like(f"%{src_ip}%"))
        if ingestion_source:
            query = query.filter(Prediction.ingestion_source == ingestion_source)
        if is_anomaly is not None:
            query = query.filter(Prediction.is_anomaly == is_anomaly)
        return query.order_by(desc(Prediction.timestamp)).offset(skip).limit(limit).all()

    def count_filtered(
        self,
        db: Session,
        is_malicious: Optional[bool] = None,
        predicted_class: Optional[str] = None,
        severity: Optional[str] = None,
        src_ip: Optional[str] = None,
        ingestion_source: Optional[str] = None,
        is_anomaly: Optional[bool] = None
    ) -> int:
        query = db.query(Prediction)
        if is_malicious is not None:
            query = query.filter(Prediction.is_malicious == is_malicious)
        if predicted_class:
            query = query.filter(Prediction.predicted_class == predicted_class)
        if severity:
            query = query.filter(Prediction.severity == severity)
        if src_ip:
            query = query.filter(Prediction.src_ip.like(f"%{src_ip}%"))
        if ingestion_source:
            query = query.filter(Prediction.ingestion_source == ingestion_source)
        if is_anomaly is not None:
            query = query.filter(Prediction.is_anomaly == is_anomaly)
        return query.count()

prediction_repo = PredictionRepository()
