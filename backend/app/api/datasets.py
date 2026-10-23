import os
import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import pandas as pd
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.models.dataset import Dataset
from app.models.user import User
from app.schemas.dataset import DatasetResponse, DatasetAnalysisResult
from app.datasets.adapters import detect_adapter
from app.datasets.bigflow_loader import BigFlowDataLoader
from app.repositories.dataset_repo import dataset_repo
from app.api.deps import get_current_user, require_analyst_or_admin

router = APIRouter(prefix="/datasets", tags=["Dataset Management"])

@router.get("", response_model=List[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    return dataset_repo.get_all(db)

@router.get("/status/bigflow")
def get_bigflow_status():
    loader = BigFlowDataLoader()
    return loader.get_dataset_summary()

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    ds = dataset_repo.get_by_id(db, dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ds

@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename must be provided.")

    clean_orig_name = os.path.basename(file.filename)
    if not clean_orig_name.lower().endswith(".csv") and not clean_orig_name.lower().endswith(".parquet"):
        raise HTTPException(status_code=400, detail="Only CSV and Parquet datasets are currently supported.")

    # Sanitize dataset name and filename to prevent path traversal (CWE-22)
    sanitized_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip())
    sanitized_filename = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", clean_orig_name)
    target_filename = f"{sanitized_name}_{sanitized_filename}"

    target_dir = os.path.abspath(settings.SAMPLE_DATASETS_DIR)
    file_path = os.path.abspath(os.path.join(target_dir, target_filename))

    # Path traversal validation
    if not file_path.startswith(target_dir + os.sep) and file_path != target_dir:
        raise HTTPException(status_code=400, detail="Invalid destination path detected.")

    # Stream file with strict MAX_UPLOAD_SIZE_BYTES limit (CWE-400 resource exhaustion mitigation)
    total_bytes = 0
    chunk_size = 1024 * 64  # 64 KB
    try:
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > settings.MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Upload size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB."
                    )
                buffer.write(chunk)
    except Exception as e:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Failed to write uploaded dataset: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while storing the uploaded dataset.")

    # Read preview to adapt & validate
    try:
        if file_path.endswith(".parquet"):
            df = pd.read_parquet(file_path)
        else:
            # Memory safety: sample preview if CSV is very large
            df = pd.read_csv(file_path, nrows=50000)

        adapter = detect_adapter(list(df.columns))
        features_df, metadata_df, y_bin, y_multi = adapter.adapt(df)

        class_dist = y_multi.value_counts().to_dict()
        benign_cnt = int((y_bin == 0).sum())
        mal_cnt = int((y_bin == 1).sum())

        col_info = [{"name": c, "dtype": str(df[c].dtype), "missing_count": int(df[c].isna().sum())} for c in df.columns[:25]]

        dataset_obj = dataset_repo.create(db, {
            "name": name,
            "description": description or f"Uploaded dataset processed via {adapter.name}",
            "adapter_type": adapter.name,
            "file_path": file_path,
            "file_size_bytes": os.path.getsize(file_path),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "benign_count": benign_cnt,
            "malicious_count": mal_cnt,
            "class_distribution": class_dist,
            "column_info": col_info,
            "is_validated": True,
            "is_sample": False
        })
        return dataset_obj
    except Exception as e:
        # Clean up file on processing failure
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        logger.error(f"Validation failed for uploaded dataset: {e}")
        raise HTTPException(status_code=400, detail=f"Dataset schema validation failed: {str(e)}")

@router.post("/{dataset_id}/analyze", response_model=DatasetAnalysisResult)
def analyze_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ds = dataset_repo.get_by_id(db, dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = ds.file_path
    if not os.path.isabs(file_path) and not os.path.exists(file_path):
        candidate = os.path.join(settings.BASE_DIR, file_path)
        if os.path.exists(candidate):
            file_path = candidate

    is_parquet_dir = os.path.isdir(file_path)
    is_parquet_file = os.path.isfile(file_path) and file_path.endswith(".parquet")
    is_large_csv = os.path.isfile(file_path) and file_path.endswith(".csv") and os.path.getsize(file_path) > 200 * 1024 * 1024

    if is_parquet_dir or is_parquet_file or is_large_csv:
        loader = BigFlowDataLoader(file_path)
        df = loader.load_stratified_sample(sample_size=10000, random_state=42)
    else:
        df = pd.read_csv(file_path)

    adapter = detect_adapter(list(df.columns))
    features_df, _, y_bin, y_multi = adapter.adapt(df)

    return DatasetAnalysisResult(
        dataset_id=ds.id,
        name=ds.name,
        total_rows=ds.total_rows if ds.total_rows > len(df) else len(df),
        total_columns=len(df.columns),
        benign_count=ds.benign_count if ds.benign_count > 0 else int((y_bin == 0).sum()),
        malicious_count=ds.malicious_count if ds.malicious_count > 0 else int((y_bin == 1).sum()),
        class_distribution=ds.class_distribution if ds.class_distribution else y_multi.value_counts().to_dict(),
        detected_adapter=adapter.name,
        detected_features=list(features_df.columns),
        missing_values_summary=df.isna().sum().to_dict()
    )

@router.delete("/{dataset_id}")
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin)
):
    ds = dataset_repo.get_by_id(db, dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    dataset_repo.delete(db, dataset_id)
    return {"message": f"Dataset {ds.name} removed successfully"}

