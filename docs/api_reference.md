# REST API Reference & Specification

Base URL: `http://localhost:8000/api`  
Interactive OpenAPI/Swagger: `http://localhost:8000/docs`

## 1. System Health & Authentication
- `GET /health`: Operational environment status, active model version, and persistence mode.
- `POST /auth/login`: Authenticate with username and password, returning JWT bearer token.
- `GET /auth/me`: Retrieve current user profile and role.

## 2. SOC Dashboard & Metrics
- `GET /dashboard`: Aggregated telemetry metrics, attack class distributions, severity profiles, top source IPs, timeline series, and federated status.

## 3. Dataset Management
- `GET /datasets`: List registered research NetFlow datasets.
- `GET /datasets/{id}`: Detailed dataset statistics.
- `POST /datasets/upload`: Upload CSV NetFlow file with multipart form-data.
- `POST /datasets/{id}/analyze`: Execute schema analysis, missing value profiling, and class distribution check.
- `DELETE /datasets/{id}`: Unregister dataset from catalog.

## 4. Model Training & Evaluation
- `GET /models`: List all trained FlowTransformer model versions.
- `GET /models/{id}`: Model architecture configuration and held-out test evaluation report.
- `POST /models/train`: Train a new FlowTransformer with custom hyperparameters and optional Random Forest baseline benchmark.
- `POST /models/{id}/activate`: Set active model for live inference.
- `GET /models/{id}/evaluation`: Retrieve per-class precision, recall, F1, and confusion matrix.

## 5. Flow Telemetry & Predictions
- `GET /predictions`: Paginated list of analyzed network flows with filtering by class, severity, and IP.
- `GET /predictions/{id}`: Deep inspection of a single flow, including eX-NIDS feature attributions and grounded evidence.
- `POST /predictions/predict`: Synchronous inference on a single flow dictionary with real-time risk scoring and alert generation.
- `POST /predictions/batch`: Batch inference on up to 100 flow records.

## 6. Alerts & Incident Management
- `GET /alerts`: Paginated security alert queue with status, severity, and category filters.
- `GET /alerts/{id}`: Detailed alert record with investigation notes and evidence.
- `PATCH /alerts/{id}`: Update alert lifecycle status, assigned analyst, or append investigation notes.
- `GET /incidents`: List declared high-priority incidents.
- `POST /incidents`: Declare new incident and correlate related alert IDs.
- `PATCH /incidents/{id}`: Update incident status, add timeline milestones, and root cause notes.

## 7. Threat Intelligence & Correlations
- `GET /iocs`: Searchable and filterable threat indicators with status separation.
- `POST /iocs`: Register custom threat indicator.
- `PATCH /iocs/{id}`: Modify verification status (unverified, confirmed_malicious, benign_whitelisted).
- `POST /cti/enrich`: Trigger AbuseIPDB / VirusTotal / offline CTI enrichment.
- `GET /correlations/graph`: Retrieve node-link threat graph data.
- `GET /mitre/techniques`: List mapped MITRE ATT&CK techniques with detection rationales.

## 8. Federated Learning Simulation
- `GET /federated/clients`: List participating sector organizations.
- `GET /federated/rounds`: History of completed federated rounds.
- `POST /federated/rounds/trigger`: Trigger simulated FedAvg training and aggregation round.

## 9. Reports & Exports
- `GET /reports/executive`: View synthesized Markdown executive report.
- `GET /reports/download`: Download `.md` report.
- `GET /cti/export/stix`: Download STIX 2.1 JSON bundle.
- `GET /cti/export/csv`: Download CSV export of threat indicators.
