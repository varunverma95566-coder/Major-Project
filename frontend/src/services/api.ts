import {
  DashboardMetrics,
  Dataset,
  MLModel,
  Prediction,
  Alert,
  Incident,
  IOC,
  GraphNode,
  GraphEdge,
  MitreTechnique,
  FederatedClient,
  FederatedRound,
  BigFlowCategoriesResponse,
  BigFlowReplayRequest,
  BigFlowReplayResponse,
  FlowFileUploadResponse,
  LiveStatusResponse,
  LiveIngestResponse
} from '../types/api';

import {
  FALLBACK_DASHBOARD_METRICS,
  FALLBACK_DATASETS,
  FALLBACK_MODELS,
  FALLBACK_IOCS,
  FALLBACK_GRAPH,
  FALLBACK_MITRE_TECHNIQUES,
  FALLBACK_FEDERATED_CLIENTS,
  FALLBACK_FEDERATED_ROUNDS,
  FALLBACK_EXECUTIVE_REPORT
} from './fallbackData';

/**
 * Returns the effective API base URL:
 * 1. User-configured override in localStorage (e.g. from Settings or Topbar modal)
 * 2. Vite environment variable VITE_API_URL
 * 3. In development mode with proxy: '/api'
 * 4. In static production hosting: '' (will detect offline and serve benchmark data)
 */
export const getApiBase = (): string => {
  const custom = localStorage.getItem('cyber_backend_url');
  if (custom && custom.trim()) {
    return custom.trim().replace(/\/$/, '');
  }
  const metaEnv = (import.meta as any).env;
  if (metaEnv?.VITE_API_URL) {
    return (metaEnv.VITE_API_URL as string).replace(/\/$/, '');
  }
  // In development, Vite server proxies /api to http://localhost:8000
  if (metaEnv?.DEV) {
    return '/api';
  }
  return '';
};

export const setApiBase = (url: string) => {
  if (!url || !url.trim()) {
    localStorage.removeItem('cyber_backend_url');
  } else {
    localStorage.setItem('cyber_backend_url', url.trim().replace(/\/$/, ''));
  }
};

export const clearApiBase = () => {
  localStorage.removeItem('cyber_backend_url');
};

export const isBackendCustomConfigured = (): boolean => {
  return !!localStorage.getItem('cyber_backend_url');
};

export const checkBackendHealth = async (customUrl?: string): Promise<{ online: boolean; details?: any; url: string }> => {
  const base = (customUrl !== undefined ? customUrl : getApiBase()).replace(/\/$/, '');
  if (!base) {
    return { online: false, url: '' };
  }
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);
    // Try both /api/health and /health depending on base URL structure
    const targetUrl = base.endsWith('/api') ? `${base}/health` : `${base}/api/health`;
    const res = await fetch(targetUrl, { signal: controller.signal });
    clearTimeout(timeoutId);
    if (res.ok) {
      const data = await res.json();
      return { online: true, details: data, url: base };
    }
    return { online: false, url: base };
  } catch {
    return { online: false, url: base };
  }
};

function getHeaders(): HeadersInit {
  const token = localStorage.getItem('cyber_token') || 'dev-analyst-token';
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

const buildUrl = (path: string): string => {
  const base = getApiBase();
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  if (!base) {
    // If no backend configured on static host, use /api prefix
    return `/api${cleanPath}`;
  }
  if (base.endsWith('/api') && cleanPath.startsWith('/api')) {
    return `${base}${cleanPath.slice(4)}`;
  }
  if (!base.endsWith('/api') && !cleanPath.startsWith('/api')) {
    return `${base}/api${cleanPath}`;
  }
  return `${base}${cleanPath}`;
};

export const api = {
  getApiBase,
  setApiBase,
  clearApiBase,
  checkBackendHealth,
  buildUrl,

  // Auth
  async login(username: string, password: string) {
    const base = getApiBase();
    const metaEnv = (import.meta as any).env;
    if (!base && !metaEnv?.DEV) {
      // Offline fallback login
      return { access_token: 'dev-analyst-token', token_type: 'bearer' };
    }
    try {
      const res = await fetch(buildUrl('/auth/login'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (!res.ok) throw new Error('Authentication failed');
      return res.json();
    } catch {
      return { access_token: 'dev-analyst-token', token_type: 'bearer' };
    }
  },

  async getMe() {
    try {
      const res = await fetch(buildUrl('/auth/me'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch user profile');
      return res.json();
    } catch {
      return {
        id: 2,
        username: 'analyst',
        email: 'analyst@cyber-soc.local',
        full_name: 'Senior SOC Analyst',
        role: 'analyst'
      };
    }
  },

  // Dashboard Metrics
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    try {
      const res = await fetch(buildUrl('/dashboard'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch dashboard metrics');
      return await res.json();
    } catch (err) {
      console.warn('Backend unavailable, serving offline benchmark dashboard metrics:', err);
      return FALLBACK_DASHBOARD_METRICS;
    }
  },

  // Datasets
  async getDatasets(): Promise<Dataset[]> {
    try {
      const res = await fetch(buildUrl('/datasets'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch datasets');
      return await res.json();
    } catch (err) {
      console.warn('Backend unavailable, serving fallback datasets:', err);
      return FALLBACK_DATASETS;
    }
  },

  async uploadDataset(formData: FormData): Promise<Dataset> {
    const token = localStorage.getItem('cyber_token') || 'dev-analyst-token';
    const res = await fetch(buildUrl('/datasets/upload'), {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload dataset. Check backend connection.');
    return res.json();
  },

  async analyzeDataset(id: number) {
    const res = await fetch(buildUrl(`/datasets/${id}/analyze`), {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to analyze dataset');
    return res.json();
  },

  // Models
  async getModels(): Promise<MLModel[]> {
    try {
      const res = await fetch(buildUrl('/models'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch models');
      return await res.json();
    } catch (err) {
      console.warn('Backend unavailable, serving benchmark models:', err);
      return FALLBACK_MODELS;
    }
  },

  async trainModel(payload: any): Promise<MLModel> {
    const res = await fetch(buildUrl('/models/train'), {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      throw new Error('Model training requires an active Python backend with PyTorch. Please connect a backend URL in Settings.');
    }
    return res.json();
  },

  async activateModel(id: number): Promise<MLModel> {
    const res = await fetch(buildUrl(`/models/${id}/activate`), {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to activate model');
    return res.json();
  },

  // Predictions & Flow Telemetry
  async getPredictions(params: Record<string, any> = {}): Promise<{ items: Prediction[]; total: number }> {
    try {
      const query = new URLSearchParams(params).toString();
      const res = await fetch(buildUrl(`/predictions?${query}`), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch predictions');
      return await res.json();
    } catch (err) {
      console.warn('Backend unavailable, serving baseline prediction telemetry:', err);
      return {
        items: [
          {
            id: 1,
            flow_id: 'flow-bf-9821',
            timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
            src_ip: '185.220.101.5',
            dst_ip: '10.0.0.15',
            dst_port: 80,
            protocol: 'TCP',
            is_malicious: true,
            predicted_class: 'DDoS',
            confidence: 0.994,
            class_probabilities: { 'DDoS': 0.994, 'BENIGN': 0.006 },
            risk_score: 96,
            severity: 'CRITICAL',
            inference_time_ms: 11.2,
            model_version: 'flow_transformer_bigflow_v2',
            feature_importances: [
              { feature: 'dst_port', value: 80, contribution: 0.42, direction: 'positive' },
              { feature: 'flow_duration', value: 3.2, contribution: 0.28, direction: 'positive' }
            ],
            model_evidence: { packet_rate: 1850.0 },
            alert_created: true
          },
          {
            id: 2,
            flow_id: 'flow-bf-9822',
            timestamp: new Date(Date.now() - 1000 * 60 * 32).toISOString(),
            src_ip: '45.33.32.156',
            dst_ip: '10.0.0.22',
            dst_port: 22,
            protocol: 'TCP',
            is_malicious: true,
            predicted_class: 'BruteForce',
            confidence: 0.984,
            class_probabilities: { 'BruteForce': 0.984, 'BENIGN': 0.016 },
            risk_score: 84,
            severity: 'HIGH',
            inference_time_ms: 10.8,
            model_version: 'flow_transformer_bigflow_v2',
            feature_importances: [
              { feature: 'dst_port', value: 22, contribution: 0.51, direction: 'positive' }
            ],
            model_evidence: { retries: 42 },
            alert_created: true
          },
          {
            id: 3,
            flow_id: 'flow-bf-9823',
            timestamp: new Date(Date.now() - 1000 * 60 * 58).toISOString(),
            src_ip: '194.26.29.112',
            dst_ip: '10.0.0.8',
            dst_port: 445,
            protocol: 'TCP',
            is_malicious: true,
            predicted_class: 'PortScan',
            confidence: 0.976,
            class_probabilities: { 'PortScan': 0.976, 'BENIGN': 0.024 },
            risk_score: 62,
            severity: 'MEDIUM',
            inference_time_ms: 11.0,
            model_version: 'flow_transformer_bigflow_v2',
            feature_importances: [
              { feature: 'dst_port', value: 445, contribution: 0.65, direction: 'positive' }
            ],
            model_evidence: { ports_scanned: 120 },
            alert_created: false
          }
        ],
        total: 3
      };
    }
  },

  async predictFlow(flow: any): Promise<Prediction> {
    const res = await fetch(buildUrl('/predictions/predict'), {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(flow)
    });
    if (!res.ok) {
      throw new Error('Flow inference requires an active Python backend. Connect a backend URL in Settings.');
    }
    return res.json();
  },

  async getBigFlowCategories(): Promise<BigFlowCategoriesResponse> {
    try {
      const res = await fetch(buildUrl('/predictions/bigflow/categories'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch BigFlow dataset categories');
      return await res.json();
    } catch {
      return {
        status: 'cached',
        total_categories: 6,
        active_model_name: 'flow_transformer_bigflow_v2',
        model_supported_count: 5,
        unsupported_count: 1,
        categories: [
          { name: 'DDoS', group: 'DoS/DDoS', is_attack: true, is_supported: true, partition_file: 'ddos_stream_part.parquet' },
          { name: 'PortScan', group: 'Reconnaissance', is_attack: true, is_supported: true, partition_file: 'portscan_stream_part.parquet' },
          { name: 'BruteForce', group: 'Authentication', is_attack: true, is_supported: true, partition_file: 'bruteforce_part.parquet' },
          { name: 'Botnet', group: 'Malware/C2', is_attack: true, is_supported: true, partition_file: 'botnet_part.parquet' },
          { name: 'WebAttack', group: 'Web Injections', is_attack: true, is_supported: true, partition_file: 'webattack_part.parquet' },
          { name: 'BENIGN', group: 'Baseline Normal', is_attack: false, is_supported: true, partition_file: 'benign_part.parquet' }
        ]
      };
    }
  },

  async replayBigFlowStream(payload: BigFlowReplayRequest): Promise<BigFlowReplayResponse> {
    const res = await fetch(buildUrl('/predictions/replay-bigflow'), {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || 'BigFlow Parquet streaming requires the active FastAPI backend. Connect backend in Settings.');
    }
    return res.json();
  },

  async uploadFlowFile(formData: FormData): Promise<FlowFileUploadResponse> {
    const token = localStorage.getItem('cyber_token') || 'dev-analyst-token';
    const res = await fetch(buildUrl('/predictions/upload-flows'), {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || 'Flow file parsing requires an active Python backend.');
    }
    return res.json();
  },

  async ingestLiveFlows(flows: any[], sensor_id: string = 'SENSOR-EDGE-01', interfaceName: string = 'eth0', create_alerts: boolean = true): Promise<LiveIngestResponse> {
    const res = await fetch(buildUrl('/predictions/live-ingest'), {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        flows,
        sensor_id,
        interface: interfaceName,
        create_alerts
      })
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || 'Live sensor ingestion requires the Python backend.');
    }
    return res.json();
  },

  async getLiveStatus(): Promise<LiveStatusResponse> {
    try {
      const res = await fetch(buildUrl('/predictions/status/live'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch live monitoring status');
      return await res.json();
    } catch {
      return {
        status: 'standby',
        interface: 'eth0',
        sensor_id: 'SENSOR-EDGE-01',
        mode: 'offline_preview',
        active_model: 'flow_transformer_bigflow_v2',
        total_live_flows_captured: 0,
        live_alerts_generated: 0
      };
    }
  },

  // Alerts
  async getAlerts(params: Record<string, any> = {}): Promise<{ items: Alert[]; total: number }> {
    try {
      const query = new URLSearchParams(params).toString();
      const res = await fetch(buildUrl(`/alerts?${query}`), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch alerts');
      return await res.json();
    } catch {
      return {
        items: FALLBACK_DASHBOARD_METRICS.recent_alerts,
        total: FALLBACK_DASHBOARD_METRICS.recent_alerts.length
      };
    }
  },

  async updateAlert(id: number, data: Partial<Alert> & { new_note?: string }): Promise<Alert> {
    const res = await fetch(buildUrl(`/alerts/${id}`), {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update alert');
    return res.json();
  },

  // Incidents
  async getIncidents(): Promise<Incident[]> {
    try {
      const res = await fetch(buildUrl('/incidents'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch incidents');
      return await res.json();
    } catch {
      return [
        {
          id: 1,
          incident_code: 'INC-2026-001',
          title: 'Volumetric Mirai Flood on Core DMZ Gateway',
          description: 'Correlated 6,420 high-frequency UDP/TCP flood flows targeting Port 80.',
          severity: 'CRITICAL',
          status: 'OPEN',
          lead_analyst: 'Senior SOC Analyst',
          affected_assets: ['10.0.0.15 (Core DMZ)'],
          associated_iocs: ['185.220.101.5'],
          mitre_tactics: ['Impact'],
          mitre_techniques: ['T1498.001'],
          timeline: [
            { timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(), event: 'Initial burst detected', user: 'FlowTransformer Engine' }
          ],
          linked_alert_count: 12,
          created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
          updated_at: new Date(Date.now() - 1000 * 60 * 45).toISOString()
        },
        {
          id: 2,
          incident_code: 'INC-2026-002',
          title: 'Distributed SSH Password Spray Campaign',
          description: 'Repeated authentication failures across Bastion gateway from known malicious IPs.',
          severity: 'HIGH',
          status: 'INVESTIGATING',
          lead_analyst: 'Senior SOC Analyst',
          affected_assets: ['10.0.0.22 (Bastion Gateway)'],
          associated_iocs: ['45.33.32.156'],
          mitre_tactics: ['Credential Access'],
          mitre_techniques: ['T1110.001'],
          timeline: [
            { timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(), event: 'Repeated Port 22 retries threshold crossed', user: 'FlowTransformer Engine' }
          ],
          linked_alert_count: 6,
          created_at: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
          updated_at: new Date(Date.now() - 1000 * 60 * 90).toISOString()
        }
      ];
    }
  },

  async createIncident(data: any): Promise<Incident> {
    const res = await fetch(buildUrl('/incidents'), {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create incident');
    return res.json();
  },

  async updateIncident(id: number, data: any): Promise<Incident> {
    const res = await fetch(buildUrl(`/incidents/${id}`), {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update incident');
    return res.json();
  },

  // IOCs & CTI
  async getIOCs(params: Record<string, any> = {}): Promise<{ items: IOC[]; total: number }> {
    try {
      const query = new URLSearchParams(params).toString();
      const res = await fetch(buildUrl(`/iocs?${query}`), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch IOCs');
      return await res.json();
    } catch {
      return {
        items: FALLBACK_IOCS,
        total: FALLBACK_IOCS.length
      };
    }
  },

  async createIOC(data: any): Promise<IOC> {
    const res = await fetch(buildUrl('/iocs'), {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create IOC');
    return res.json();
  },

  async updateIOC(id: number, data: any): Promise<IOC> {
    const res = await fetch(buildUrl(`/iocs/${id}`), {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update IOC');
    return res.json();
  },

  async enrichIndicator(target: string) {
    try {
      const res = await fetch(buildUrl(`/cti/enrich?target=${encodeURIComponent(target)}`), {
        method: 'POST',
        headers: getHeaders()
      });
      if (!res.ok) throw new Error('Enrichment failed');
      return await res.json();
    } catch {
      return {
        target,
        risk_score: 92,
        is_malicious: true,
        threat_actors: ['UNC2452 / APT29'],
        malware_families: ['Mirai-Variant-X', 'Mozi Botnet'],
        sources: ['AlienVault OTX', 'MISP Threat Sharing', 'AbuseIPDB Verified']
      };
    }
  },

  async getCorrelationGraph(): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
    try {
      const res = await fetch(buildUrl('/correlations/graph'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch threat graph');
      return await res.json();
    } catch {
      return FALLBACK_GRAPH;
    }
  },

  async getMitreTechniques(): Promise<MitreTechnique[]> {
    try {
      const res = await fetch(buildUrl('/mitre/techniques'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch MITRE techniques');
      return await res.json();
    } catch {
      return FALLBACK_MITRE_TECHNIQUES;
    }
  },

  // Federated Learning
  async getFederatedClients(): Promise<FederatedClient[]> {
    try {
      const res = await fetch(buildUrl('/federated/clients'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch federated clients');
      return await res.json();
    } catch {
      return FALLBACK_FEDERATED_CLIENTS;
    }
  },

  async getFederatedRounds(): Promise<FederatedRound[]> {
    try {
      const res = await fetch(buildUrl('/federated/rounds'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch federated rounds');
      return await res.json();
    } catch {
      return FALLBACK_FEDERATED_ROUNDS;
    }
  },

  async triggerFederatedRound(payload: any = {}): Promise<FederatedRound> {
    const res = await fetch(buildUrl('/federated/rounds/trigger'), {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Federated aggregation requires the Python backend.');
    return res.json();
  },

  // Reports
  async getExecutiveReport(): Promise<{ report_markdown: string }> {
    try {
      const res = await fetch(buildUrl('/reports/executive'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch report');
      return await res.json();
    } catch {
      return { report_markdown: FALLBACK_EXECUTIVE_REPORT };
    }
  },

  // Settings
  async getSettings() {
    try {
      const res = await fetch(buildUrl('/settings/integrations'), { headers: getHeaders() });
      if (!res.ok) throw new Error('Failed to fetch settings');
      return await res.json();
    } catch {
      return {
        database: {
          engine: 'SQLite / PostgreSQL Ready',
          url_configured: 'sqlite:///./data/nids_platform.db'
        },
        compute: {
          device: 'CUDA / PyTorch CPU',
          transformer_threads: 8,
          active_model: 'flow_transformer_bigflow_v2'
        },
        cti: {
          alienvault_otx: 'Connected (Demo Key)',
          misp: 'Connected',
          virustotal: 'Ready'
        }
      };
    }
  }
};
