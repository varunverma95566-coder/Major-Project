# Transformer-Based Network Intrusion Detection & Cyber Threat Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.14%2Bcpu-red.svg)](https://pytorch.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.156-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-cyan.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4-purple.svg)](https://vitejs.dev)
[![STIX](https://img.shields.io/badge/STIX-2.1%20Compliant-orange.svg)](https://oasis-open.github.io/cti-documentation/)
[![MITRE](https://img.shields.io/badge/MITRE%20ATT%26CK-v14.1-blue.svg)](https://attack.mitre.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, AI-powered cybersecurity platform that analyzes network telemetry, classifies traffic as **NORMAL** or **MALICIOUS** using a real PyTorch Transformer-based NIDS model, identifies attack categories dynamically across 32 attack classes from the **BigFlow-NIDS** dataset, detects **Open-Set Anomalies**, and enriches detections with **Cyber Threat Intelligence (CTI)**, threat correlation graphs, and privacy-preserving **Federated Learning**.

---

## 🚀 Key Architectural Capabilities

### 1. Multi-Modal Flow Ingestion with Strict Provenance
- **BigFlow-NIDS Replay (`dataset_replay`):** Replays representative flow records from 67 merged Parquet partitions of the 66.9M-flow BigFlow-NIDS-V2 benchmark directly through the FlowTransformer engine.
- **Genuine Live Ingestion (`live_capture`):** Real-time sensor listener interface (`GET /api/predictions/status/live`, `POST /api/predictions/live-ingest`) evaluating unlabelled network telemetry from physical/virtual perimeter interfaces (e.g. `eth0` / `SENSOR-EDGE-01`).
- **Memory-Safe File Upload (`file_upload`):** Batch ingestion interface (`POST /api/predictions/upload-flows`) parsing `.csv` (CICFlowMeter/Zeek), `.parquet`, and `.json` flow files in memory-safe chunks with automatic schema adaptation.
- **Simulated Presets (`simulated_preset`):** Preset demonstration buttons clearly tagged with provenance disclaimer badges; predictions are always derived objectively by the neural network logits.

### 2. Dual-Head FlowTransformer with Open-Set Anomaly Detection
- **Transformer Encoder:** Projects tabular continuous NetFlow features through a learned linear projection layer ($d_{model}=64$) with learned categorical embeddings, LayerNorm, and 4 multi-head self-attention heads across 2 Transformer encoder layers.
- **Dual Classification Heads:**
  1. *Binary Head:* High-sensitivity detection of malicious vs. benign behavior.
  2. *Multiclass Head:* Softmax classification across active model attack classes.
- **Open-Set Anomaly Handling:** When the binary head flags high-conviction malicious traffic but the multiclass head exhibits low confidence ($< 0.40$) or maps to Benign, the traffic is classified as `"Unknown / Suspicious Anomaly"` with `is_anomaly=True`.
- **Ground-Truth Independence:** Dataset labels are strictly recorded in `ground_truth_attack` for post-inference verification and are never leaked into model inputs.

### 3. Cyber Threat Intelligence (CTI) & Explainable AI (eX-NIDS)
- **CTI Enrichment:** Integrates AbuseIPDB, VirusTotal, and offline threat feeds with verified reputation scoring and STIX 2.1 JSON bundle exports.
- **MITRE ATT&CK Mapping:** Links inferred attack vectors to tactics and techniques (e.g., T1498 for Network Denial of Service, T1110 for Brute Force, T1046 for Network Service Discovery).
- **Multi-Factor Risk Scoring:** Synthesizes model confidence, category severity weights, target port criticality, and CTI reputation scores into a 0–100 risk score.
- **eX-NIDS Saliency:** Feature sensitivity attributions computed via $\text{Input} \times \text{Gradient}$ formulation, grounding natural language explanations directly in observed telemetry.

### 4. Collaborative Federated Defense
- Implements privacy-preserving Federated Averaging (FedAvg) across simulated banking, healthcare, and telecom sector nodes.
- Nodes train locally on private NetFlow partitions; only model weight parameters are transmitted to the coordinator.

---

## 🛠️ Project Structure

```
Major Project/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints (predictions, alerts, CTI, dashboard, federated)
│   │   ├── core/            # Configuration, database connection, security, logging
│   │   ├── cti/             # Threat intelligence feeds, IP enrichment, risk scoring, STIX 2.1
│   │   ├── datasets/        # Schema adapters (BigFlow, CICFlowMeter, NetFlow) & preprocessor
│   │   ├── ml/              # PyTorch FlowTransformer architecture, inference, explainability
│   │   ├── models/          # SQLAlchemy ORM models (Prediction, Alert, Incident, IOC, MLModel)
│   │   ├── repositories/    # Database query abstractions and filtering
│   │   ├── schemas/         # Pydantic validation schemas
│   │   └── seed/            # Seeder for demo users, model records, alerts, and MITRE data
│   ├── artifacts/           # Trained FlowTransformer weights and preprocessors
│   ├── requirements.txt     # Python dependencies
│   └── tests/               # Pytest automated test suite (38 passing tests)
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components, Badges, Modals, Navbar, StatCards
│   │   ├── context/         # AuthContext and ToastContext
│   │   ├── pages/           # Dashboard, TrafficAnalysis, FlowInvestigation, Alerts, CTI, Federated
│   │   ├── services/        # Frontend API client methods
│   │   └── types/           # TypeScript interfaces and API schemas
│   ├── package.json         # Node.js dependencies
│   └── vite.config.ts       # Vite build & proxy configuration
├── data/                    # Local SQLite database (git-ignored) & export directories
├── docs/                    # Architecture diagrams, API reference, guides, and PDF reports
├── docker-compose.yml       # Docker Compose multi-container deployment
├── Dockerfile.backend       # Backend Docker container specification
├── Dockerfile.frontend      # Frontend Docker container specification
└── README.md
```

---

## 💻 Quickstart & Local Setup

### Prerequisites
- **Python 3.10+** (Tested on Python 3.11 & 3.14)
- **Node.js 18+** & **npm**

---

### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Seed development database with active model checkpoint & MITRE techniques
python -m app.seed.seeder

# Start the FastAPI backend server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

* Backend API will be live at: **`http://localhost:8000`**
* Interactive Swagger UI docs: **`http://localhost:8000/docs`**
* Health check: **`http://localhost:8000/api/health`**

---

### Step 2: Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

* SOC Dashboard will be live at: **`http://localhost:5173`**

---

### Default Credentials
- **Analyst:** `username: analyst@defense.soc` | `password: Password123!`
- **Admin:** `username: admin@defense.soc` | `password: Password123!`
- **Quick Access:** Click *"Enter as SOC Analyst (Dev Mode)"* on the login screen.

---

## 🧪 Automated Test Suite

Run the full automated test suite verifying preprocessing, model inference, CTI enrichment, file upload, live ingestion, federated aggregation, and ground-truth isolation:

```bash
cd backend
python -m pytest tests/
```

*All 38 automated unit and integration tests execute deterministically on CPU.*

---

## 📦 Dataset Acquisition (BigFlow-NIDS)

The **BigFlow-NIDS-V2** dataset contains 66.9 million network flows partitioned into 67 Parquet files (~3 GB total). Due to size limits on GitHub, raw parquet partitions are omitted from git tracking.

To enable full local parquet streaming:
1. Download the **BigFlow-NIDS-V2-Merged-Parquet** partition files from the official repository.
2. Place the parquet files into:
   ```
   BigFlow-NIDS/BigFlow-NIDS-V2-Merged-Parquet/merged_part_0.parquet ... merged_part_66.parquet
   ```
3. If parquet partitions are absent, the platform automatically utilizes its embedded fallback telemetry streaming engine for all 32 attack categories.

---

## 🐳 Docker Deployment

To launch the full stack (backend, frontend, database) using Docker:

```bash
docker-compose up --build
```

- Frontend: `http://localhost:5173`
- Backend API Docs: `http://localhost:8000/docs`

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
