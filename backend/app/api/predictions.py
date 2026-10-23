import io
import os
import re
import uuid
import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import pandas as pd

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.ml_model import MLModel
from app.models.cti import IOC
from app.schemas.prediction import (
    PredictionResponse,
    FlowFeatureInput,
    BatchPredictionRequest,
    BigFlowCategoriesResponse,
    BigFlowCategoryItem,
    BigFlowReplayRequest,
    BigFlowReplayResponse,
    BigFlowReplayItem,
    FeatureImportanceItem,
    FlowFileUploadResponse,
    LiveIngestRequest,
    LiveIngestResponse,
    LiveStatusResponse
)
from app.schemas.common import PaginatedResponse
from app.repositories.prediction_repo import prediction_repo
from app.repositories.model_repo import model_repo
from app.ml.inference import inference_service
from app.cti.risk_scoring import calculate_risk_score
from app.cti.mitre_mapper import map_attack_to_mitre
from app.cti.ioc_extractor import extract_iocs_from_flow
from app.cti.enrichment import enrichment_service
from app.datasets.adapters import detect_adapter
from app.datasets.bigflow_loader import BigFlowDataLoader

router = APIRouter(prefix="/predictions", tags=["Inference & Flow Investigation"])


def _sanitize_for_json(data: Any) -> Any:
    """Recursively converts timestamps, numpy scalars, and NaN values into JSON-serializable primitives."""
    if data is None:
        return None
    if isinstance(data, dict):
        return {k: _sanitize_for_json(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [_sanitize_for_json(v) for v in data]
    if hasattr(data, "isoformat"):
        return data.isoformat()
    if hasattr(data, "item"):
        return data.item()
    if isinstance(data, float) and (data != data or data == float('inf') or data == float('-inf')):
        return None
    return data


@router.get("", response_model=PaginatedResponse[PredictionResponse])
def list_flows(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    is_malicious: Optional[bool] = None,
    predicted_class: Optional[str] = None,
    severity: Optional[str] = None,
    src_ip: Optional[str] = None,
    ingestion_source: Optional[str] = None,
    is_anomaly: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    items = prediction_repo.filter_flows(
        db, skip=skip, limit=page_size,
        is_malicious=is_malicious,
        predicted_class=predicted_class,
        severity=severity,
        src_ip=src_ip,
        ingestion_source=ingestion_source,
        is_anomaly=is_anomaly
    )
    total = prediction_repo.count_filtered(
        db,
        is_malicious=is_malicious,
        predicted_class=predicted_class,
        severity=severity,
        src_ip=src_ip,
        ingestion_source=ingestion_source,
        is_anomaly=is_anomaly
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse(
        items=[PredictionResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/status/live", response_model=LiveStatusResponse)
def get_live_monitoring_status(db: Session = Depends(get_db)):
    """Returns status and metrics for the real-time live flow monitoring collector."""
    active_m = model_repo.get_active_model(db)
    live_count = db.query(Prediction).filter(Prediction.ingestion_source == "live_capture").count()
    live_alerts = (
        db.query(Alert)
        .join(Prediction, Alert.prediction_id == Prediction.id)
        .filter(Prediction.ingestion_source == "live_capture")
        .count()
    )
    latest_live = (
        db.query(Prediction)
        .filter(Prediction.ingestion_source == "live_capture")
        .order_by(Prediction.timestamp.desc())
        .first()
    )

    return LiveStatusResponse(
        status="active",
        interface="eth0 (Live Flow Ingestion Interface)",
        sensor_id="SENSOR-CORE-01",
        mode="continuous_monitoring",
        active_model=active_m.name if active_m else "flow_transformer_bigflow_v2",
        total_live_flows_captured=live_count,
        live_alerts_generated=live_alerts,
        last_capture_time=latest_live.timestamp if latest_live else None
    )


@router.get("/bigflow/categories", response_model=BigFlowCategoriesResponse)
def get_bigflow_categories(db: Session = Depends(get_db)):
    """Returns verified dataset attack categories from BigFlow-NIDS with model support indicators."""
    active_m = model_repo.get_active_model(db)
    active_classes = active_m.target_classes if active_m else []

    loader = BigFlowDataLoader()
    categories = loader.get_verified_categories(active_model_classes=active_classes)

    supported_count = sum(1 for c in categories if c["is_supported"])
    unsupported_count = sum(1 for c in categories if not c["is_supported"])

    return BigFlowCategoriesResponse(
        status="ready" if loader.parquet_files else "sample_fallback",
        total_categories=len(categories),
        active_model_name=active_m.name if active_m else None,
        model_supported_count=supported_count,
        unsupported_count=unsupported_count,
        categories=[BigFlowCategoryItem(**c) for c in categories]
    )


@router.get("/{prediction_id}", response_model=PredictionResponse)
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    p = prediction_repo.get_by_id(db, prediction_id)
    if not p:
        raise HTTPException(status_code=404, detail="Prediction record not found")
    return p


@router.post("/predict", response_model=PredictionResponse)
def predict_single_flow(
    flow_input: FlowFeatureInput,
    create_alert_if_malicious: bool = True,
    db: Session = Depends(get_db)
):
    """Processes a flow through the real Transformer model, enriches with CTI, and records results."""
    # Ensure active model loaded in memory
    if inference_service.model is None:
        active_m = model_repo.get_active_model(db)
        if not active_m:
            raise HTTPException(status_code=400, detail="No active FlowTransformer model found in database. Train or activate a model first.")
        success = inference_service.load_model(active_m.name)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to load weights for active model '{active_m.name}'.")

    # Build input dictionary
    flow_dict = flow_input.model_dump()
    if flow_input.features:
        flow_dict.update(flow_input.features)

    # 1. CTI Enrichment: query threat reputation for source IP
    src_ip = str(flow_input.src_ip or "192.168.1.100")
    cti_info = enrichment_service.enrich_ip(src_ip)
    rep_score = cti_info.get("reputation_score", 0)

    # 2. Transformer Inference & Open-Set Anomaly Detection
    infer_res = inference_service.predict_flow(flow_dict)

    # 3. Risk Scoring Engine with CTI reputation
    risk_score, severity, risk_rationale = calculate_risk_score(
        predicted_class=infer_res["predicted_class"],
        confidence=infer_res["confidence"],
        dst_port=flow_input.dst_port,
        reputation_score=rep_score
    )

    # 4. MITRE Mapping
    mitre_data = map_attack_to_mitre(infer_res["predicted_class"], flow_dict)

    # 5. Save Prediction Record
    flow_uuid = f"FLOW-{uuid.uuid4().hex[:12].upper()}"
    active_m = model_repo.get_active_model(db)
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    ingest_source = flow_input.ingestion_source or ("simulated_preset" if flow_input.is_simulated else "live_capture")
    dataset_source = flow_input.dataset_source or ("Simulated Preset" if flow_input.is_simulated else "Live Telemetry Feed")

    clean_features = _sanitize_for_json(flow_dict)
    clean_probs = _sanitize_for_json(infer_res.get("class_probabilities", {}))
    clean_importances = _sanitize_for_json(infer_res.get("feature_importances", []))
    clean_evidence = _sanitize_for_json(infer_res.get("model_evidence", {}))

    pred_record = prediction_repo.create(db, {
        "flow_id": flow_uuid,
        "timestamp": now_utc,
        "src_ip": flow_input.src_ip,
        "dst_ip": flow_input.dst_ip,
        "src_port": flow_input.src_port,
        "dst_port": flow_input.dst_port,
        "protocol": flow_input.protocol,
        "flow_features": clean_features,
        "model_id": active_m.id if active_m else None,
        "model_version": infer_res["model_version"],
        "is_malicious": infer_res["is_malicious"],
        "predicted_class": infer_res["predicted_class"],
        "confidence": infer_res["confidence"],
        "class_probabilities": clean_probs,
        "inference_time_ms": infer_res["inference_time_ms"],
        "risk_score": risk_score,
        "severity": severity,
        "feature_importances": clean_importances,
        "human_explanation": infer_res["human_explanation"],
        "model_evidence": clean_evidence,
        "llm_interpretation": infer_res["llm_interpretation"],
        "alert_created": False,
        "ingestion_source": ingest_source,
        "is_anomaly": infer_res.get("is_anomaly", False),
        "is_simulated": bool(flow_input.is_simulated),
        "ground_truth_attack": flow_input.ground_truth_attack,
        "dataset_source": dataset_source
    })

    # 6. Extract IOCs & Create Alert if Malicious or Anomaly
    if infer_res["is_malicious"] and create_alert_if_malicious:
        alert_code = f"ALT-2026-{db.query(Alert).count() + 1:04d}"
        alert_title = f"{infer_res['predicted_class']} Activity Detected from {flow_input.src_ip}"
        if infer_res.get("is_anomaly"):
            alert_title = f"Unknown Suspicious Anomaly from {flow_input.src_ip}"

        alert_evidence = infer_res.get("model_evidence", {}).copy() if isinstance(infer_res.get("model_evidence"), dict) else {}
        alert_evidence["cti_enrichment"] = {
            "provider": cti_info.get("provider"),
            "verification_status": cti_info.get("verification_status"),
            "reputation_score": cti_info.get("reputation_score"),
            "country": cti_info.get("country"),
            "asn": cti_info.get("asn"),
            "threat_types": cti_info.get("threat_types", [])
        }

        alert_obj = Alert(
            alert_code=alert_code,
            title=alert_title,
            description=infer_res["human_explanation"],
            category=infer_res["predicted_class"],
            severity=severity,
            risk_score=risk_score,
            confidence=infer_res["confidence"],
            src_ip=flow_input.src_ip,
            dst_ip=flow_input.dst_ip,
            src_port=flow_input.src_port,
            dst_port=flow_input.dst_port,
            protocol=flow_input.protocol,
            prediction_id=pred_record.id,
            mitre_technique_id=mitre_data["technique_id"],
            status="New",
            evidence=_sanitize_for_json(alert_evidence),
            investigation_notes=[{
                "timestamp": now_utc.isoformat(),
                "author": "Autonomous FlowTransformer Engine",
                "note": (
                    f"Flow flagged as {infer_res['predicted_class']} ({infer_res['confidence']*100:.1f}% confidence). "
                    f"CTI from {cti_info.get('provider')}: verification '{cti_info.get('verification_status')}', "
                    f"reputation {rep_score}/100, ASN: {cti_info.get('asn')}."
                )
            }]
        )

        db.add(alert_obj)
        pred_record.alert_created = True
        db.commit()

        # Extract IOCs and preserve CTI verification status
        extracted_iocs = extract_iocs_from_flow(flow_dict)
        for ioc_in in extracted_iocs:
            existing_ioc = db.query(IOC).filter(IOC.value == ioc_in["value"]).first()
            if not existing_ioc:
                if ioc_in.get("value") == src_ip:
                    ioc_in["reputation_score"] = rep_score
                    ioc_in["verification_status"] = cti_info.get("verification_status", ioc_in["verification_status"])
                    ioc_in["enrichment_data"] = cti_info
                ioc_record = IOC(**ioc_in)
                ioc_record.related_alert_count = 1
                db.add(ioc_record)
            else:
                existing_ioc.related_alert_count = (existing_ioc.related_alert_count or 0) + 1
        db.commit()

    return pred_record


@router.post("/batch")
def predict_batch_flows(request: BatchPredictionRequest, db: Session = Depends(get_db)):
    results = []
    for flow in request.flows[:100]:  # Limit batch to 100 for responsive request loop
        if request.ingestion_source:
            flow.ingestion_source = request.ingestion_source
        res = predict_single_flow(flow, create_alert_if_malicious=request.create_alerts, db=db)
        results.append(res)
    return {"processed_count": len(results), "items": results}


@router.post("/live-ingest", response_model=LiveIngestResponse)
def ingest_live_flows(
    request: LiveIngestRequest,
    db: Session = Depends(get_db)
):
    """Ingests genuine live network flow records from monitoring probes or active network interfaces."""
    processed_items = []
    mal_cnt = 0
    ben_cnt = 0
    anom_cnt = 0

    for flow in request.flows[:100]:
        flow.ingestion_source = "live_capture"
        flow.is_simulated = False
        flow.dataset_source = f"Live Monitor ({request.interface})"
        res = predict_single_flow(flow, create_alert_if_malicious=request.create_alerts, db=db)
        if res.is_malicious:
            mal_cnt += 1
        else:
            ben_cnt += 1
        if res.is_anomaly:
            anom_cnt += 1
        processed_items.append(PredictionResponse.model_validate(res))

    return LiveIngestResponse(
        status="success",
        sensor_id=request.sensor_id or "SENSOR-EDGE-01",
        interface=request.interface or "eth0",
        ingested_count=len(processed_items),
        malicious_count=mal_cnt,
        benign_count=ben_cnt,
        anomaly_count=anom_cnt,
        items=processed_items
    )


@router.post("/upload-flows", response_model=FlowFileUploadResponse)
async def upload_flow_file_for_detection(
    file: UploadFile = File(...),
    create_alerts: bool = Form(True),
    max_flows: int = Form(100),
    db: Session = Depends(get_db)
):
    """Processes an uploaded network flow file (CSV, Parquet, JSON) through FlowTransformer."""
    # Ensure active model loaded
    if inference_service.model is None:
        active_m = model_repo.get_active_model(db)
        if not active_m:
            raise HTTPException(status_code=400, detail="No active FlowTransformer model found in database.")
        inference_service.load_model(active_m.name)

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected for upload.")

    clean_filename = os.path.basename(file.filename)
    ext = clean_filename.lower().split(".")[-1]
    if ext not in ["csv", "parquet", "json"]:
        raise HTTPException(status_code=400, detail="Only CSV, Parquet, and JSON flow files are supported.")

    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Upload size exceeds {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB."
        )

    try:
        if ext == "parquet":
            df_raw = pd.read_parquet(io.BytesIO(contents))
        elif ext == "json":
            df_raw = pd.read_json(io.BytesIO(contents))
        else:
            df_raw = pd.read_csv(io.BytesIO(contents), nrows=min(max_flows * 5, 2000), low_memory=False)
    except Exception as e:
        logger.error(f"Failed to parse uploaded flow file {clean_filename}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse flow file: {str(e)}")

    if len(df_raw) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file contains zero flow records.")

    # Detect adapter to normalize schema
    adapter = detect_adapter(list(df_raw.columns))
    features_df, metadata_df, y_bin, y_multi = adapter.adapt(df_raw.head(max_flows))

    processed_items = []
    mal_cnt = 0
    ben_cnt = 0
    anom_cnt = 0
    alerts_cnt = 0

    for idx in range(len(features_df)):
        flow_rec = features_df.iloc[idx].to_dict()
        meta_rec = metadata_df.iloc[idx].to_dict()
        flow_rec.update(meta_rec)

        # Ground truth (if available in file) is recorded for evaluation comparison, never copied to prediction
        gt_attack = str(y_multi.iloc[idx]) if idx < len(y_multi) else None

        flow_input = FlowFeatureInput(
            src_ip=str(meta_rec.get("src_ip", "192.168.1.100")),
            dst_ip=str(meta_rec.get("dst_ip", "10.0.0.5")),
            src_port=int(meta_rec.get("src_port", 49152)),
            dst_port=int(meta_rec.get("dst_port", 80)),
            protocol=str(meta_rec.get("protocol", "TCP")),
            ingestion_source="file_upload",
            is_simulated=False,
            ground_truth_attack=gt_attack,
            dataset_source=f"Uploaded File ({clean_filename})",
            features=flow_rec
        )

        res = predict_single_flow(flow_input, create_alert_if_malicious=create_alerts, db=db)
        if res.is_malicious:
            mal_cnt += 1
        else:
            ben_cnt += 1
        if res.is_anomaly:
            anom_cnt += 1
        if res.alert_created:
            alerts_cnt += 1

        processed_items.append(PredictionResponse.model_validate(res))

    active_m = model_repo.get_active_model(db)
    return FlowFileUploadResponse(
        filename=clean_filename,
        total_parsed=len(df_raw),
        processed_count=len(processed_items),
        malicious_count=mal_cnt,
        benign_count=ben_cnt,
        anomaly_count=anom_cnt,
        alerts_created=alerts_cnt,
        adapter_applied=adapter.name,
        model_version=active_m.name if active_m else "FlowTransformer",
        items=processed_items
    )


@router.post("/replay-bigflow", response_model=BigFlowReplayResponse)
def replay_bigflow_stream(
    request: BigFlowReplayRequest,
    db: Session = Depends(get_db)
):
    """Streams and evaluates real representative records from BigFlow-NIDS through FlowTransformer."""
    # Ensure active model loaded
    active_m = model_repo.get_active_model(db)
    if inference_service.model is None:
        if not active_m:
            raise HTTPException(status_code=400, detail="No active FlowTransformer model found. Please activate or train a model.")
        success = inference_service.load_model(active_m.name)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to load weights for active model '{active_m.name}'.")

    active_classes = set(active_m.target_classes if (active_m and active_m.target_classes) else [])

    loader = BigFlowDataLoader()
    batch_records = loader.get_category_sample_records(
        category=request.category,
        limit=request.batch_size
    )

    if not batch_records:
        raise HTTPException(
            status_code=404,
            detail=f"No representative records found in BigFlow-NIDS for category '{request.category}'."
        )

    processed_items = []
    malicious_count = 0
    benign_count = 0
    correct_on_supported = 0
    total_supported = 0

    for rec in batch_records:
        gt_attack = str(rec.get("ground_truth_attack") or "Unknown")
        gt_label = int(rec.get("ground_truth_label", 1 if gt_attack != "Benign" else 0))
        is_gt_malicious = (gt_label == 1 or gt_attack.lower() != "benign")

        src_ip = str(rec.get("src_ip") or rec.get("IPV4_SRC_ADDR") or "192.168.1.100")
        dst_ip = str(rec.get("dst_ip") or rec.get("IPV4_DST_ADDR") or "10.0.0.1")
        try:
            src_port = int(rec.get("src_port") or rec.get("L4_SRC_PORT") or 49152)
        except Exception:
            src_port = 49152
        try:
            dst_port = int(rec.get("dst_port") or rec.get("L4_DST_PORT") or 80)
        except Exception:
            dst_port = 80
        protocol = str(rec.get("protocol") or rec.get("PROTOCOL") or "TCP")
        dataset_source = str(rec.get("dataset_source") or "BigFlow-NIDS-V2")

        # Execute through the model inference pipeline
        infer_res = inference_service.predict_flow(rec)

        # CTI enrichment
        cti_info = enrichment_service.enrich_ip(src_ip)
        rep_score = cti_info.get("reputation_score", 0)

        # Risk scoring
        risk_score, severity, risk_rationale = calculate_risk_score(
            predicted_class=infer_res["predicted_class"],
            confidence=infer_res["confidence"],
            dst_port=dst_port,
            reputation_score=rep_score
        )

        # Check if category is supported by the active model
        is_supported = gt_attack in active_classes
        is_match = (infer_res["predicted_class"].lower() == gt_attack.lower())

        if is_supported:
            total_supported += 1
            if is_match:
                correct_on_supported += 1
            unsupported_warn = None
        else:
            unsupported_warn = (
                f"'{gt_attack}' is present in BigFlow-NIDS dataset but was omitted from active model's {len(active_classes)}-class "
                f"training partition. Model classified as closest latent class '{infer_res['predicted_class']}'. Retraining required."
            )

        if infer_res["is_malicious"]:
            malicious_count += 1
        else:
            benign_count += 1

        # Persist prediction in database with full provenance
        flow_uuid = f"FLOW-BF-{uuid.uuid4().hex[:10].upper()}"
        now_utc = datetime.datetime.now(datetime.timezone.utc)

        clean_features = _sanitize_for_json(rec)
        clean_evidence = _sanitize_for_json(infer_res.get("model_evidence", {}))
        clean_importances = _sanitize_for_json(infer_res.get("feature_importances", []))
        clean_probs = _sanitize_for_json(infer_res.get("class_probabilities", {}))

        pred_record = prediction_repo.create(db, {
            "flow_id": flow_uuid,
            "timestamp": now_utc,
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": protocol,
            "flow_features": clean_features,
            "model_id": active_m.id if active_m else None,
            "model_version": infer_res["model_version"],
            "is_malicious": infer_res["is_malicious"],
            "predicted_class": infer_res["predicted_class"],
            "confidence": infer_res["confidence"],
            "class_probabilities": clean_probs,
            "inference_time_ms": infer_res["inference_time_ms"],
            "risk_score": risk_score,
            "severity": severity,
            "feature_importances": clean_importances,
            "human_explanation": infer_res["human_explanation"],
            "model_evidence": clean_evidence,
            "llm_interpretation": infer_res["llm_interpretation"],
            "alert_created": False,
            "ingestion_source": "dataset_replay",
            "is_anomaly": infer_res.get("is_anomaly", False),
            "is_simulated": False,
            "ground_truth_attack": gt_attack,
            "dataset_source": dataset_source
        })

        alert_created = False
        # Create alert if malicious & requested
        if infer_res["is_malicious"] and request.create_alerts:
            mitre_data = map_attack_to_mitre(infer_res["predicted_class"], rec)
            alert_code = f"ALT-2026-{db.query(Alert).count() + 1:04d}"
            alert_title = f"BigFlow Alert: {infer_res['predicted_class']} from {src_ip} ({dataset_source})"
            if infer_res.get("is_anomaly"):
                alert_title = f"BigFlow Anomaly: Unknown Threat Pattern from {src_ip}"

            alert_evidence = infer_res.get("model_evidence", {}).copy() if isinstance(infer_res.get("model_evidence"), dict) else {}
            alert_evidence["cti_enrichment"] = {
                "provider": cti_info.get("provider"),
                "verification_status": cti_info.get("verification_status"),
                "reputation_score": cti_info.get("reputation_score"),
                "country": cti_info.get("country"),
                "asn": cti_info.get("asn"),
                "threat_types": cti_info.get("threat_types", [])
            }

            alert_obj = Alert(
                alert_code=alert_code,
                title=alert_title,
                description=f"Ground Truth: {gt_attack}. {infer_res['human_explanation']}",
                category=infer_res["predicted_class"],
                severity=severity,
                risk_score=risk_score,
                confidence=infer_res["confidence"],
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol=protocol,
                prediction_id=pred_record.id,
                mitre_technique_id=mitre_data["technique_id"],
                status="New",
                evidence=_sanitize_for_json(alert_evidence),
                investigation_notes=[{
                    "timestamp": now_utc.isoformat(),
                    "author": "BigFlow Replay Engine",
                    "note": (
                        f"Evaluated BigFlow-NIDS record with Ground Truth '{gt_attack}'. "
                        f"Model inferred '{infer_res['predicted_class']}' ({infer_res['confidence']*100:.1f}% confidence). "
                        f"CTI: {cti_info.get('provider')} (status: {cti_info.get('verification_status')})."
                    )
                }]
            )
            db.add(alert_obj)
            pred_record.alert_created = True
            db.commit()
            alert_created = True

            # Extract IOCs
            extracted_iocs = extract_iocs_from_flow(rec)
            for ioc_in in extracted_iocs:
                existing_ioc = db.query(IOC).filter(IOC.value == ioc_in["value"]).first()
                if not existing_ioc:
                    if ioc_in.get("value") == src_ip:
                        ioc_in["reputation_score"] = rep_score
                        ioc_in["verification_status"] = cti_info.get("verification_status", ioc_in["verification_status"])
                        ioc_in["enrichment_data"] = cti_info
                    ioc_record = IOC(**ioc_in)
                    ioc_record.related_alert_count = 1
                    db.add(ioc_record)
                else:
                    existing_ioc.related_alert_count = (existing_ioc.related_alert_count or 0) + 1
            db.commit()

        # Format feature importances
        f_items = [
            FeatureImportanceItem(**fi) if isinstance(fi, dict) else fi
            for fi in infer_res.get("feature_importances", [])
        ]

        processed_items.append(BigFlowReplayItem(
            flow_id=flow_uuid,
            timestamp=now_utc,
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=protocol,
            ground_truth_attack=gt_attack,
            ground_truth_label=gt_label,
            is_ground_truth_malicious=is_gt_malicious,
            predicted_class=infer_res["predicted_class"],
            confidence=infer_res["confidence"],
            is_malicious=infer_res["is_malicious"],
            model_version=infer_res["model_version"] or (active_m.name if active_m else "FlowTransformer"),
            model_supported=is_supported,
            is_correct_prediction=is_match,
            unsupported_warning=unsupported_warn,
            risk_score=risk_score,
            severity=severity,
            inference_time_ms=infer_res["inference_time_ms"],
            feature_importances=f_items,
            human_explanation=infer_res["human_explanation"],
            dataset_source=dataset_source,
            alert_created=alert_created,
            is_anomaly=infer_res.get("is_anomaly", False),
            ingestion_source="dataset_replay",
            is_simulated=False
        ))

    acc_supported = round(correct_on_supported / max(total_supported, 1), 4) if total_supported > 0 else None

    return BigFlowReplayResponse(
        category_requested=request.category,
        processed_count=len(processed_items),
        malicious_count=malicious_count,
        benign_count=benign_count,
        accuracy_on_supported=acc_supported,
        items=processed_items
    )
