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

const API_BASE = '/api';

function getHeaders(): HeadersInit {
  const token = localStorage.getItem('cyber_token') || 'dev-analyst-token';
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

export const api = {
  // Auth
  async login(username: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) throw new Error('Authentication failed');
    return res.json();
  },

  async getMe() {
    const res = await fetch(`${API_BASE}/auth/me`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch user profile');
    return res.json();
  },

  // Dashboard
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const res = await fetch(`${API_BASE}/dashboard`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch dashboard metrics');
    return res.json();
  },

  // Datasets
  async getDatasets(): Promise<Dataset[]> {
    const res = await fetch(`${API_BASE}/datasets`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch datasets');
    return res.json();
  },

  async uploadDataset(formData: FormData): Promise<Dataset> {
    const token = localStorage.getItem('cyber_token') || 'dev-analyst-token';
    const res = await fetch(`${API_BASE}/datasets/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload dataset');
    return res.json();
  },

  async analyzeDataset(id: number) {
    const res = await fetch(`${API_BASE}/datasets/${id}/analyze`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to analyze dataset');
    return res.json();
  },

  // Models
  async getModels(): Promise<MLModel[]> {
    const res = await fetch(`${API_BASE}/models`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch models');
    return res.json();
  },

  async trainModel(payload: any): Promise<MLModel> {
    const res = await fetch(`${API_BASE}/models/train`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Model training request failed');
    return res.json();
  },

  async activateModel(id: number): Promise<MLModel> {
    const res = await fetch(`${API_BASE}/models/${id}/activate`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to activate model');
    return res.json();
  },

  // Predictions & Flow Telemetry
  async getPredictions(params: Record<string, any> = {}): Promise<{ items: Prediction[]; total: number }> {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/predictions?${query}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch predictions');
    return res.json();
  },

  async predictFlow(flow: any): Promise<Prediction> {
    const res = await fetch(`${API_BASE}/predictions/predict`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(flow)
    });
    if (!res.ok) throw new Error('Prediction execution failed');
    return res.json();
  },

  async getBigFlowCategories(): Promise<BigFlowCategoriesResponse> {
    const res = await fetch(`${API_BASE}/predictions/bigflow/categories`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch BigFlow dataset categories');
    return res.json();
  },

  async replayBigFlowStream(payload: BigFlowReplayRequest): Promise<BigFlowReplayResponse> {
    const res = await fetch(`${API_BASE}/predictions/replay-bigflow`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to replay BigFlow stream');
    }
    return res.json();
  },

  async uploadFlowFile(formData: FormData): Promise<FlowFileUploadResponse> {
    const token = localStorage.getItem('cyber_token') || 'dev-analyst-token';
    const res = await fetch(`${API_BASE}/predictions/upload-flows`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to process uploaded flow file');
    }
    return res.json();
  },

  async ingestLiveFlows(flows: any[], sensor_id: string = 'SENSOR-EDGE-01', interfaceName: string = 'eth0', create_alerts: boolean = true): Promise<LiveIngestResponse> {
    const res = await fetch(`${API_BASE}/predictions/live-ingest`, {
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
      throw new Error(errData.detail || 'Failed to ingest live flow telemetry');
    }
    return res.json();
  },

  async getLiveStatus(): Promise<LiveStatusResponse> {
    const res = await fetch(`${API_BASE}/predictions/status/live`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch live monitoring status');
    return res.json();
  },

  // Alerts
  async getAlerts(params: Record<string, any> = {}): Promise<{ items: Alert[]; total: number }> {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/alerts?${query}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  async updateAlert(id: number, data: Partial<Alert> & { new_note?: string }): Promise<Alert> {
    const res = await fetch(`${API_BASE}/alerts/${id}`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update alert');
    return res.json();
  },

  // Incidents
  async getIncidents(): Promise<Incident[]> {
    const res = await fetch(`${API_BASE}/incidents`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch incidents');
    return res.json();
  },

  async createIncident(data: any): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create incident');
    return res.json();
  },

  async updateIncident(id: number, data: any): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents/${id}`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update incident');
    return res.json();
  },

  // IOCs & CTI
  async getIOCs(params: Record<string, any> = {}): Promise<{ items: IOC[]; total: number }> {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/iocs?${query}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch IOCs');
    return res.json();
  },

  async createIOC(data: any): Promise<IOC> {
    const res = await fetch(`${API_BASE}/iocs`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create IOC');
    return res.json();
  },

  async updateIOC(id: number, data: any): Promise<IOC> {
    const res = await fetch(`${API_BASE}/iocs/${id}`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update IOC');
    return res.json();
  },

  async enrichIndicator(target: string) {
    const res = await fetch(`${API_BASE}/cti/enrich?target=${encodeURIComponent(target)}`, {
      method: 'POST',
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Enrichment failed');
    return res.json();
  },

  async getCorrelationGraph(): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
    const res = await fetch(`${API_BASE}/correlations/graph`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch threat graph');
    return res.json();
  },

  async getMitreTechniques(): Promise<MitreTechnique[]> {
    const res = await fetch(`${API_BASE}/mitre/techniques`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch MITRE techniques');
    return res.json();
  },

  // Federated Learning
  async getFederatedClients(): Promise<FederatedClient[]> {
    const res = await fetch(`${API_BASE}/federated/clients`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch federated clients');
    return res.json();
  },

  async getFederatedRounds(): Promise<FederatedRound[]> {
    const res = await fetch(`${API_BASE}/federated/rounds`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch federated rounds');
    return res.json();
  },

  async triggerFederatedRound(payload: any = {}): Promise<FederatedRound> {
    const res = await fetch(`${API_BASE}/federated/rounds/trigger`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to trigger federated round');
    return res.json();
  },

  // Reports
  async getExecutiveReport(): Promise<{ report_markdown: string }> {
    const res = await fetch(`${API_BASE}/reports/executive`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch report');
    return res.json();
  },

  // Settings
  async getSettings() {
    const res = await fetch(`${API_BASE}/settings/integrations`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch settings');
    return res.json();
  }
};
