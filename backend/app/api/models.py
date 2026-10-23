from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.ml_model import MLModel
from app.models.dataset import Dataset
from app.schemas.ml import MLModelResponse, TrainModelRequest, EvaluationMetrics
from app.repositories.model_repo import model_repo
from app.repositories.dataset_repo import dataset_repo
from app.ml.trainer import train_flow_transformer_pipeline
from app.ml.inference import inference_service

import re
from app.models.user import User
from app.core.logging import logger
from app.api.deps import require_analyst_or_admin

router = APIRouter(prefix="/models", tags=["Model Management"])

@router.get("", response_model=List[MLModelResponse])
def list_models(db: Session = Depends(get_db)):
    return model_repo.get_all(db)

@router.get("/{model_id}", response_model=MLModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    m = model_repo.get_by_id(db, model_id)
    if not m:
        raise HTTPException(status_code=404, detail="Model not found")
    return m

@router.post("/train", response_model=MLModelResponse)
def train_model(
    request: TrainModelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)
):
    # Sanitize model name to prevent path traversal in model directory
    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", request.name.strip())
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid model name provided.")

    ds = dataset_repo.get_by_id(db, request.dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        # Run training pipeline
        meta = train_flow_transformer_pipeline(
            dataset_path=ds.file_path,
            model_name=safe_name,
            epochs=request.epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate,
            train_baseline=request.train_baseline,
            architecture_config=request.architecture.model_dump()
        )
    except Exception as e:
        logger.error(f"Model training pipeline failed for '{safe_name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Training pipeline execution failed: {str(e)}")

    metrics = meta.get("metrics", {})
    baseline = meta.get("baseline_metrics", {})

    model_data = {
        "name": safe_name,
        "version": "1.0.0",
        "model_type": "FlowTransformer",
        "description": request.description,
        "dataset_id": ds.id,
        "architecture_config": meta.get("architecture_config", {}),
        "weights_path": meta.get("weights_path"),
        "preprocessor_path": meta.get("preprocessor_path"),
        "target_classes": meta.get("target_classes", []),
        "status": "trained",
        "is_active": True,  # automatically set as active
        "accuracy": metrics.get("accuracy"),
        "precision": metrics.get("precision"),
        "recall": metrics.get("recall"),
        "f1_score": metrics.get("f1_score"),
        "per_class_metrics": metrics.get("per_class_metrics", {}),
        "confusion_matrix": metrics.get("confusion_matrix", []),
        "training_history": meta.get("history", {}),
        "baseline_metrics": baseline
    }

    existing_model = model_repo.get_by_name(db, safe_name)
    if existing_model:
        model_record = model_repo.update(db, existing_model.id, model_data)
    else:
        model_record = model_repo.create(db, model_data)


    # Activate in inference service
    inference_service.load_model(safe_name)
    model_repo.set_active_model(db, model_record.id)

    return model_record

@router.post("/{model_id}/activate", response_model=MLModelResponse)
def activate_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)
):
    m = model_repo.get_by_id(db, model_id)
    if not m:
        raise HTTPException(status_code=404, detail="Model not found")
    
    success = inference_service.load_model(m.name)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to load model weights.")
    
    updated = model_repo.set_active_model(db, model_id)
    return updated


@router.get("/{model_id}/evaluation", response_model=EvaluationMetrics)
def get_model_evaluation(model_id: int, db: Session = Depends(get_db)):
    m = model_repo.get_by_id(db, model_id)
    if not m:
        raise HTTPException(status_code=404, detail="Model not found")

    return EvaluationMetrics(
        accuracy=m.accuracy or 0.0,
        precision=m.precision or 0.0,
        recall=m.recall or 0.0,
        f1_score=m.f1_score or 0.0,
        per_class_metrics=m.per_class_metrics or {},
        confusion_matrix=m.confusion_matrix or [],
        classes=m.target_classes or []
    )
