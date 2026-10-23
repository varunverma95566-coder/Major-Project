# System Architecture & Processing Pipeline

## 1. End-to-End Flow Pipeline

The platform ingests network telemetry and executes a continuous 14-stage defensive security pipeline:

```
Network Traffic / Uploaded NetFlow CSV
  │
  ▼
[1. Input Validation & Schema Sanitization]
  │
  ▼
[2. NetFlow Adapter Normalization (NF-UNSW-NB15-v2, NF-BoT-IoT-v2, Edge-IIoTset)]
  │
  ▼
[3. Missing Value Imputation & Outlier Handling]
  │
  ▼
[4. Feature Tokenization & Learned Embedding Projection (d_model=64)]
  │
  ▼
[5. Multi-Head Self-Attention Transformer Encoder (2 Layers, 4 Heads)]
  │
  ▼
[6. Dual Classification Heads: Binary Maliciousness + Multiclass Attack Category]
  │
  ▼
[7. eX-NIDS Explainability: Input x Gradient Feature Attributions]
  │
  ▼
[8. IOC Extraction: IP, Domain, Port Validation & Status Separation]
  │
  ▼
[9. CTI Threat Enrichment: Reputation Scoring (AbuseIPDB / Offline DB)]
  │
  ▼
[10. MITRE ATT&CK Mapping: Tactic, Technique ID, Detection Rationale]
  │
  ▼
[11. Multi-Factor Risk Scoring Engine (0 to 100 Normalized Severity)]
  │
  ▼
[12. Alert Lifecycle & Incident Correlation Engine]
  │
  ▼
[13. Collaborative Federated Defense Simulation (FedAvg Parameter Aggregation)]
  │
  ▼
[14. SOC Dashboard, STIX 2.1 Export & Audit Logging]
```

## 2. Machine Learning Architecture (FlowTransformer)

- **Feature Tokenizer**: Tabular continuous features are projected via learned linear weights into $d_{model}=64$, accompanied by learned categorical embeddings and tabular position identifiers.
- **Transformer Encoder**: 2 encoder layers featuring 4 attention heads each, LayerNorm, and ReLU feedforward sub-layers.
- **Binary Classification Head**: Sigmoid-activated logit outputting benign vs malicious probability.
- **Multiclass Classification Head**: Softmax distribution across dataset-supported attack vectors.
- **Loss Function**: Combined loss $\mathcal{L} = \mathcal{L}_{BCE} + \mathcal{L}_{Weighted-CE}$ with inverse-frequency class weighting to eliminate imbalance bias.
- **Baseline Comparison**: Scikit-Learn `RandomForestClassifier` fitted on the identical training split for empirical benchmarking.

## 3. Explainability Subsystem (eX-NIDS)

- **Feature Sensitivity**: Computes $\text{Attribution}_i = x_i \cdot \frac{\partial \hat{y}}{\partial x_i}$ across all continuous flow features.
- **Grounded Natural-Language Generator**: Synthesizes explanatory text strictly bound to observed telemetry.
- **Optional LLM Interface**: Decoupled interface allowing plug-in of OpenAI / Anthropic keys without overriding verified mathematical evidence.

## 4. Federated Learning Coordinator

- Implements standard Federated Averaging (FedAvg):
$$\theta_{global}^{t+1} = \sum_{k=1}^K \frac{n_k}{N} \theta_k^{t+1}$$
- Privacy preservation: Only model parameter weights/deltas are transferred; raw packet flow records remain strictly localized within participant environments.
