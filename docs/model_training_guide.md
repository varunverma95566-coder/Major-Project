# Model Training & Evaluation Guide

## 1. FlowTransformer Architecture Details

The FlowTransformer is an engineering adaptation of Transformer encoders specifically tailored for tabular NetFlow traffic.

### Recommended Hyperparameters
- **Embedding Dimension ($d_{model}$)**: 64 (divisible by attention heads).
- **Multi-Head Self-Attention Heads ($h$)**: 4.
- **Encoder Layers ($L$)**: 2.
- **Feedforward Hidden Dim**: 128.
- **Dropout**: 0.10.
- **Optimizer**: AdamW ($\text{lr}=10^{-3}$, weight decay $=10^{-4}$).
- **Batch Size**: 32 or 64.
- **Epochs**: 3 to 10 for rapid CPU convergence.

## 2. Training Pipeline Execution

### Via REST API:
```bash
curl -X POST http://localhost:8000/api/models/train \
  -H "Content-Type: application/json" \
  -d '{
    "name": "flow_transformer_prod",
    "dataset_id": 1,
    "epochs": 5,
    "batch_size": 64,
    "train_baseline": true,
    "architecture": {
      "embedding_dim": 64,
      "num_heads": 4,
      "num_layers": 2,
      "dropout": 0.1
    }
  }'
```

### Via CLI Script:
```bash
python -c "from app.core.config import settings; from app.ml.trainer import train_flow_transformer_pipeline; train_flow_transformer_pipeline(settings.BIGFLOW_NIDS_PARQUET_DIR, 'flow_transformer_bigflow_v2', epochs=5, architecture_config={'sample_size': 10000})"
```

## 3. Artifact Storage

Trained artifacts are structured under `backend/artifacts/models/<model_name>/`:
- `weights.pt`: PyTorch model state dictionary.
- `preprocessor.json`: Fitted scaler parameters, categorical mappings, and class weights.
- `metadata.json`: Architecture config, evaluation metrics on held-out test split, and baseline comparisons.
