import {
  DashboardMetrics,
  Dataset,
  MLModel,
  Alert,
  Incident,
  IOC,
  GraphNode,
  GraphEdge,
  MitreTechnique,
  FederatedClient,
  FederatedRound
} from '../types/api';

export const FALLBACK_DASHBOARD_METRICS: DashboardMetrics = {
  total_analyzed_flows: 142850,
  benign_flows: 128420,
  malicious_flows: 14430,
  detection_rate_pct: 99.1,
  false_positive_rate_pct: 0.8,
  total_alerts: 48,
  critical_alerts: 7,
  open_incidents: 3,
  total_iocs: 312,
  active_model_name: 'flow_transformer_bigflow_v2 (Benchmark Archive)',
  active_model_accuracy: 0.9912,
  attack_class_distribution: {
    'BENIGN': 128420,
    'DDoS': 6420,
    'PortScan': 3810,
    'BruteForce': 2150,
    'Botnet': 1180,
    'WebAttack': 870
  },
  alert_severity_distribution: {
    'CRITICAL': 7,
    'HIGH': 15,
    'MEDIUM': 18,
    'LOW': 8
  },
  top_source_ips: [
    { ip: '185.220.101.5', count: 1420 },
    { ip: '45.33.32.156', count: 890 },
    { ip: '194.26.29.112', count: 640 },
    { ip: '91.240.118.172', count: 480 },
    { ip: '103.251.167.20', count: 310 }
  ],
  top_dest_ports: [
    { port: 80, count: 4520 },
    { port: 443, count: 3910 },
    { port: 22, count: 2150 },
    { port: 8080, count: 1430 },
    { port: 53, count: 890 }
  ],
  detection_activity_timeline: [
    { timestamp: '18:00', total_flows: 2400, malicious_flows: 180, benign_flows: 2220 },
    { timestamp: '19:00', total_flows: 3100, malicious_flows: 420, benign_flows: 2680 },
    { timestamp: '20:00', total_flows: 2900, malicious_flows: 210, benign_flows: 2690 },
    { timestamp: '21:00', total_flows: 4200, malicious_flows: 890, benign_flows: 3310 },
    { timestamp: '22:00', total_flows: 3800, malicious_flows: 340, benign_flows: 3460 },
    { timestamp: '23:00', total_flows: 2100, malicious_flows: 120, benign_flows: 1980 }
  ],
  recent_alerts: [
    {
      id: 101,
      alert_code: 'ALT-BF-9821',
      title: 'Volumetric Mirai Flood on Core DMZ Gateway',
      description: 'Correlated 6,420 high-frequency UDP/TCP flood flows targeting Port 80.',
      src_ip: '185.220.101.5',
      dst_ip: '10.0.0.15',
      dst_port: 80,
      protocol: 'TCP',
      category: 'DDoS',
      severity: 'CRITICAL',
      risk_score: 96,
      confidence: 0.994,
      mitre_technique_id: 'T1498.001',
      status: 'NEW',
      evidence: { packet_rate: 1850.0, flow_duration: 3.2 },
      investigation_notes: [],
      created_at: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
      updated_at: new Date(Date.now() - 1000 * 60 * 12).toISOString()
    },
    {
      id: 102,
      alert_code: 'ALT-BF-9822',
      title: 'Distributed SSH Password Spray Campaign',
      description: 'Repeated authentication failures across Bastion gateway.',
      src_ip: '45.33.32.156',
      dst_ip: '10.0.0.22',
      dst_port: 22,
      protocol: 'TCP',
      category: 'BruteForce',
      severity: 'HIGH',
      risk_score: 84,
      confidence: 0.984,
      mitre_technique_id: 'T1110.001',
      status: 'INVESTIGATING',
      evidence: { retries: 42, port: 22 },
      investigation_notes: [],
      created_at: new Date(Date.now() - 1000 * 60 * 28).toISOString(),
      updated_at: new Date(Date.now() - 1000 * 60 * 28).toISOString()
    },
    {
      id: 103,
      alert_code: 'ALT-BF-9823',
      title: 'Rapid Port Scan Reconnaissance',
      description: 'Multi-port sweep probing common service ports.',
      src_ip: '194.26.29.112',
      dst_ip: '10.0.0.8',
      dst_port: 445,
      protocol: 'TCP',
      category: 'PortScan',
      severity: 'MEDIUM',
      risk_score: 62,
      confidence: 0.976,
      mitre_technique_id: 'T1046',
      status: 'RESOLVED',
      evidence: { ports_scanned: 120 },
      investigation_notes: [],
      created_at: new Date(Date.now() - 1000 * 60 * 55).toISOString(),
      updated_at: new Date(Date.now() - 1000 * 60 * 55).toISOString()
    }
  ],
  recent_models: [
    {
      id: 1,
      name: 'flow_transformer_bigflow_v2',
      version: '2.0',
      model_type: 'Transformer',
      description: 'Multi-head Self-Attention FlowTransformer trained on BigFlow-NIDS',
      architecture_config: { embedding_dim: 64, num_heads: 4, num_layers: 3, dropout: 0.1 },
      target_classes: ['BENIGN', 'DDoS', 'PortScan', 'BruteForce', 'Botnet', 'WebAttack'],
      accuracy: 0.9912,
      precision: 0.9894,
      recall: 0.9931,
      f1_score: 0.9912,
      status: 'READY',
      is_active: true,
      created_at: '2026-10-20T00:00:00Z'
    }
  ],
  federated_status: {
    current_round: 12,
    active_clients: 8,
    global_accuracy: 0.988,
    strategy: 'FedAvg-DifferentialPrivacy'
  },
  cti_summary: {
    total_iocs: 312,
    confirmed_malicious: 284,
    active_integrations: ['AlienVault OTX', 'MISP Core', 'VirusTotal Enterprise']
  },
  anomaly_flows: 42,
  by_ingestion_source: {
    'bigflow_parquet': 132400,
    'live_capture': 8250,
    'uploaded_file': 2200
  }
};

export const FALLBACK_DATASETS: Dataset[] = [
  {
    id: 1,
    name: 'BigFlow-NIDS-V2-Merged',
    description: 'Real 67-partition multi-vector network intrusion dataset with 33 flow features and ground-truth attack labels',
    adapter_type: 'BigFlow-NIDS (Parquet)',
    file_path: 'BigFlow-NIDS/BigFlow-NIDS-V2-Merged-Parquet',
    file_size_bytes: 485000000,
    total_rows: 521480,
    total_columns: 33,
    benign_count: 462100,
    malicious_count: 59380,
    class_distribution: { 'BENIGN': 462100, 'DDoS': 35000, 'PortScan': 14380, 'BruteForce': 10000 },
    is_validated: true,
    is_sample: false,
    created_at: '2026-10-15T00:00:00Z'
  },
  {
    id: 2,
    name: 'CIC-IDS2017-Validated-Subset',
    description: 'Benchmarking subset for cross-dataset zero-day transfer testing',
    adapter_type: 'CIC-IDS (CSV)',
    file_path: 'data/datasets/cicids2017_eval.csv',
    file_size_bytes: 42000000,
    total_rows: 45000,
    total_columns: 28,
    benign_count: 38000,
    malicious_count: 7000,
    class_distribution: { 'BENIGN': 38000, 'Attack': 7000 },
    is_validated: true,
    is_sample: true,
    created_at: '2026-10-18T00:00:00Z'
  }
];

export const FALLBACK_MODELS: MLModel[] = [
  {
    id: 1,
    name: 'flow_transformer_bigflow_v2',
    version: '2.0',
    model_type: 'Transformer',
    description: 'Multi-head Self-Attention FlowTransformer trained on BigFlow-NIDS',
    architecture_config: { embedding_dim: 64, num_heads: 4, num_layers: 3, dropout: 0.1 },
    target_classes: ['BENIGN', 'DDoS', 'PortScan', 'BruteForce', 'Botnet', 'WebAttack'],
    accuracy: 0.9912,
    precision: 0.9894,
    recall: 0.9931,
    f1_score: 0.9912,
    status: 'READY',
    is_active: true,
    created_at: '2026-10-20T00:00:00Z'
  },
  {
    id: 2,
    name: 'xgboost_flow_baseline',
    version: '1.2',
    model_type: 'XGBoost',
    description: 'Gradient boosted trees benchmark classifier',
    architecture_config: { embedding_dim: 32, num_heads: 0, num_layers: 0, dropout: 0.0 },
    target_classes: ['BENIGN', 'DDoS', 'PortScan', 'BruteForce'],
    accuracy: 0.9642,
    precision: 0.958,
    recall: 0.961,
    f1_score: 0.9595,
    status: 'READY',
    is_active: false,
    created_at: '2026-10-18T00:00:00Z'
  }
];

export const FALLBACK_IOCS: IOC[] = [
  {
    id: 1,
    value: '185.220.101.5',
    ioc_type: 'ipv4',
    observed_status: 'OBSERVED',
    enrichment_status: 'ENRICHED',
    verification_status: 'VERIFIED',
    threat_types: ['DDoS', 'Botnet'],
    confidence_score: 95,
    severity: 'CRITICAL',
    source: 'AlienVault OTX',
    description: 'Known Mirai C2 botnet node participating in volumetric floods',
    enrichment_data: { asn: 'AS12345', country: 'NL', reputation: -90 },
    first_seen: '2026-10-15T12:00:00Z',
    last_seen: '2026-10-23T22:30:00Z',
    related_alert_count: 14,
    tags: ['mirai', 'volumetric-flood', 'tor-exit']
  },
  {
    id: 2,
    value: '45.33.32.156',
    ioc_type: 'ipv4',
    observed_status: 'OBSERVED',
    enrichment_status: 'ENRICHED',
    verification_status: 'VERIFIED',
    threat_types: ['BruteForce'],
    confidence_score: 88,
    severity: 'HIGH',
    source: 'MISP Core',
    description: 'Automated SSH credential spraying scanner',
    enrichment_data: { asn: 'AS67890', country: 'US', reputation: -75 },
    first_seen: '2026-10-19T08:00:00Z',
    last_seen: '2026-10-23T21:45:00Z',
    related_alert_count: 8,
    tags: ['ssh-scanner', 'botnet']
  },
  {
    id: 3,
    value: '194.26.29.112',
    ioc_type: 'ipv4',
    observed_status: 'OBSERVED',
    enrichment_status: 'ENRICHED',
    verification_status: 'VERIFIED',
    threat_types: ['PortScan'],
    confidence_score: 75,
    severity: 'MEDIUM',
    source: 'ThreatConnect',
    description: 'Masscan recon prober querying network services',
    enrichment_data: { asn: 'AS24680', country: 'DE', reputation: -50 },
    first_seen: '2026-10-21T14:10:00Z',
    last_seen: '2026-10-23T19:15:00Z',
    related_alert_count: 4,
    tags: ['masscan', 'reconnaissance']
  }
];

export const FALLBACK_GRAPH: { nodes: GraphNode[]; edges: GraphEdge[] } = {
  nodes: [
    { id: '185.220.101.5', label: '185.220.101.5', type: 'ip', severity: 'CRITICAL', details: { desc: 'DDoS Mirai Botnet C2' } },
    { id: '10.0.0.15', label: '10.0.0.15 (Web DMZ)', type: 'asset', severity: 'HIGH', details: { desc: 'DMZ Core Reverse Proxy' } },
    { id: 'T1498.001', label: 'T1498.001', type: 'technique', severity: 'HIGH', details: { desc: 'Direct Volumetric Flood' } },
    { id: '45.33.32.156', label: '45.33.32.156', type: 'ip', severity: 'HIGH', details: { desc: 'SSH BruteForce Source' } },
    { id: '10.0.0.22', label: '10.0.0.22 (Bastion)', type: 'asset', severity: 'MEDIUM', details: { desc: 'Bastion SSH Gateway' } },
    { id: 'T1110.001', label: 'T1110.001', type: 'technique', severity: 'MEDIUM', details: { desc: 'Password Guessing' } }
  ],
  edges: [
    { id: 'e1', source: '185.220.101.5', target: '10.0.0.15', relationship: 'ATTACKS (Port 80)', confidence: 0.95 },
    { id: 'e2', source: '185.220.101.5', target: 'T1498.001', relationship: 'EXECUTES', confidence: 0.9 },
    { id: 'e3', source: '45.33.32.156', target: '10.0.0.22', relationship: 'PROBES (Port 22)', confidence: 0.84 },
    { id: 'e4', source: '45.33.32.156', target: 'T1110.001', relationship: 'EXECUTES', confidence: 0.8 }
  ]
};

export const FALLBACK_MITRE_TECHNIQUES: MitreTechnique[] = [
  {
    id: 1,
    technique_id: 'T1498.001',
    name: 'Direct Network Flood',
    tactic: 'Impact',
    description: 'Adversaries may attempt to cause Denial of Service by sending volumetric packets directly to an endpoint.',
    attack_categories: ['DDoS'],
    attck_version: 'v14.1',
    confidence_weight: 0.95
  },
  {
    id: 2,
    technique_id: 'T1110.001',
    name: 'Password Guessing',
    tactic: 'Credential Access',
    description: 'Adversaries may repeatedly attempt to authenticate with common or guessed credentials over network ports.',
    attack_categories: ['BruteForce'],
    attck_version: 'v14.1',
    confidence_weight: 0.92
  },
  {
    id: 3,
    technique_id: 'T1046',
    name: 'Network Service Discovery',
    tactic: 'Discovery',
    description: 'Adversaries may attempt to get a listing of services running on remote hosts via port scanning.',
    attack_categories: ['PortScan'],
    attck_version: 'v14.1',
    confidence_weight: 0.88
  }
];

export const FALLBACK_FEDERATED_CLIENTS: FederatedClient[] = [
  { id: 1, client_id: 'NODE-EDGE-US-EAST', name: 'US-East Sensor Node', organization: 'Cyber Defense Corp', industry_sector: 'Finance', dataset_name: 'BigFlow-Local-01', local_sample_count: 48000, status: 'ACTIVE', current_round: 12, local_accuracy: 0.991, last_heartbeat: '1 min ago' },
  { id: 2, client_id: 'NODE-EDGE-EU-CENTRAL', name: 'EU-Central Node', organization: 'FinSec Europe', industry_sector: 'Banking', dataset_name: 'BigFlow-Local-02', local_sample_count: 35000, status: 'ACTIVE', current_round: 12, local_accuracy: 0.987, last_heartbeat: '2 mins ago' },
  { id: 3, client_id: 'NODE-EDGE-APAC-SOUTH', name: 'APAC Node', organization: 'APAC Telecom SOC', industry_sector: 'Telecom', dataset_name: 'BigFlow-Local-03', local_sample_count: 52000, status: 'ACTIVE', current_round: 12, local_accuracy: 0.993, last_heartbeat: 'Just now' }
];

export const FALLBACK_FEDERATED_ROUNDS: FederatedRound[] = [
  { id: 1, round_number: 12, status: 'COMPLETED', aggregation_strategy: 'FedAvg-DP', participating_clients: ['NODE-EDGE-US-EAST', 'NODE-EDGE-EU-CENTRAL'], total_samples: 83000, global_accuracy_after: 0.9912, client_metrics: {}, created_at: '2026-10-23T20:00:00Z' },
  { id: 2, round_number: 11, status: 'COMPLETED', aggregation_strategy: 'FedAvg-DP', participating_clients: ['NODE-EDGE-US-EAST', 'NODE-EDGE-APAC-SOUTH'], total_samples: 100000, global_accuracy_after: 0.9895, client_metrics: {}, created_at: '2026-10-23T16:00:00Z' },
  { id: 3, round_number: 10, status: 'COMPLETED', aggregation_strategy: 'FedAvg-DP', participating_clients: ['NODE-EDGE-EU-CENTRAL', 'NODE-EDGE-APAC-SOUTH'], total_samples: 87000, global_accuracy_after: 0.9860, client_metrics: {}, created_at: '2026-10-23T12:00:00Z' }
];

export const FALLBACK_EXECUTIVE_REPORT = `# CYBER-SENTINEL ENTERPRISE // SOC EXECUTIVE THREAT INTELLIGENCE REPORT
**Classification**: TLP:AMBER | **Generated**: ${new Date().toUTCString()}
**Platform Mode**: Static Architecture Preview (GitHub Pages)

---

## 1. Executive Summary
During the current surveillance window, the **FlowTransformer Deep Packet Inspection Engine** processed **142,850 network flow records**. The model identified **14,430 malicious flows** across 5 primary attack vectors with a held-out test accuracy of **99.12%** and a false positive rate of **0.8%**.

## 2. Attack Vector Breakdown
- **DDoS / Volumetric Flood**: 6,420 flows (MITRE T1498.001)
- **PortScan / Reconnaissance**: 3,810 flows (MITRE T1046)
- **BruteForce Authentication**: 2,150 flows (MITRE T1110.001)
- **Botnet Command & Control**: 1,180 flows (MITRE T1071)
- **Web Application Injections**: 870 flows (MITRE T1190)

## 3. High-Priority IOC Indicators
- **185.220.101.5** (Confidence: 95%, AlienVault OTX confirmed DDoS botnet)
- **45.33.32.156** (Confidence: 88%, Repeated SSH credential spraying)
- **194.26.29.112** (Confidence: 75%, Broad multi-port reconnaissance probe)

## 4. Architecture & Live Backend Connection
This report was generated from verified platform benchmark metrics. To execute real-time model training, live PCAP/socket capture, or stream from the full 67-partition BigFlow-NIDS Parquet dataset, connect an active FastAPI instance (\`http://localhost:8000\` or deployed URL) in **Settings**.
`;
