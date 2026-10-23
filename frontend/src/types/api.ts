export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: string;
}

export interface DashboardMetrics {
  total_analyzed_flows: number;
  benign_flows: number;
  malicious_flows: number;
  detection_rate_pct: number;
  false_positive_rate_pct: number;
  total_alerts: number;
  critical_alerts: number;
  open_incidents: number;
  total_iocs: number;
  active_model_name?: string;
  active_model_accuracy?: number;
  attack_class_distribution: Record<string, number>;
  alert_severity_distribution: Record<string, number>;
  top_source_ips: Array<{ ip: string; count: number }>;
  top_dest_ports: Array<{ port: number; count: number }>;
  detection_activity_timeline: Array<{
    timestamp: string;
    total_flows: number;
    malicious_flows: number;
    benign_flows: number;
  }>;
  recent_alerts: Alert[];
  recent_models: MLModel[];
  federated_status: {
    current_round: number;
    active_clients: number;
    global_accuracy: number;
    strategy: string;
  };
  cti_summary: {
    total_iocs: number;
    confirmed_malicious: number;
    active_integrations: string[];
  };
  anomaly_flows?: number;
  by_ingestion_source?: Record<string, number>;
}


export interface Dataset {
  id: number;
  name: string;
  description?: string;
  adapter_type: string;
  file_path: string;
  file_size_bytes: number;
  total_rows: number;
  total_columns: number;
  benign_count: number;
  malicious_count: number;
  column_info?: Array<{ name: string; dtype: string; missing_count: number }>;
  class_distribution: Record<string, number>;
  is_validated: boolean;
  is_sample: boolean;
  created_at: string;
}

export interface MLModel {
  id: number;
  name: string;
  version: string;
  model_type: string;
  description?: string;
  architecture_config: {
    embedding_dim: number;
    num_heads: number;
    num_layers: number;
    dropout: number;
    feedforward_dim?: number;
  };
  target_classes: string[];
  status: string;
  is_active: boolean;
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  per_class_metrics?: Record<string, { precision: number; recall: number; f1_score: number; support: number }>;
  confusion_matrix?: number[][];
  training_history?: {
    train_loss: number[];
    val_loss: number[];
    val_accuracy: number[];
  };
  baseline_metrics?: {
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    binary_accuracy?: number;
  };
  created_at: string;
}

export interface FeatureImportanceItem {
  feature: string;
  value: any;
  contribution: number;
  direction: string;
}

export interface Prediction {
  id: number;
  flow_id: string;
  timestamp: string;
  src_ip?: string;
  dst_ip?: string;
  src_port?: number;
  dst_port?: number;
  protocol?: string;
  is_malicious: boolean;
  predicted_class: string;
  confidence: number;
  class_probabilities: Record<string, number>;
  risk_score: number;
  severity: string;
  inference_time_ms: number;
  model_version?: string;
  feature_importances: FeatureImportanceItem[];
  human_explanation?: string;
  model_evidence: Record<string, any>;
  llm_interpretation?: string;
  alert_created: boolean;
  ingestion_source?: string;
  is_anomaly?: boolean;
  is_simulated?: boolean;
  ground_truth_attack?: string;
  dataset_source?: string;
}

export interface FlowFileUploadResponse {
  filename: string;
  total_parsed: number;
  processed_count: number;
  malicious_count: number;
  benign_count: number;
  anomaly_count: number;
  alerts_created: number;
  adapter_applied: string;
  model_version: string;
  items: Prediction[];
}

export interface LiveStatusResponse {
  status: string;
  interface: string;
  sensor_id: string;
  mode: string;
  active_model?: string;
  total_live_flows_captured: number;
  live_alerts_generated: number;
  last_capture_time?: string;
}

export interface LiveIngestResponse {
  status: string;
  sensor_id: string;
  interface: string;
  ingested_count: number;
  malicious_count: number;
  benign_count: number;
  anomaly_count: number;
  items: Prediction[];
}

export interface Alert {
  id: number;
  alert_code: string;
  title: string;
  description?: string;
  category: string;
  severity: string;
  risk_score: number;
  confidence: number;
  src_ip?: string;
  dst_ip?: string;
  src_port?: number;
  dst_port?: number;
  protocol?: string;
  prediction_id?: number;
  incident_id?: number;
  mitre_technique_id?: string;
  status: string;
  assigned_to?: string;
  resolution_notes?: string;
  evidence: Record<string, any>;
  investigation_notes: Array<{ timestamp: string; author: string; note: string }>;
  created_at: string;
  updated_at: string;
}

export interface Incident {
  id: number;
  incident_code: string;
  title: string;
  description?: string;
  severity: string;
  status: string;
  lead_analyst?: string;
  affected_assets: string[];
  associated_iocs: string[];
  mitre_tactics: string[];
  mitre_techniques: string[];
  root_cause?: string;
  mitigation_steps?: string;
  timeline: Array<{ timestamp: string; event: string; user: string }>;
  linked_alert_count: number;
  created_at: string;
  updated_at: string;
}

export interface IOC {
  id: number;
  value: string;
  ioc_type: string;
  observed_status: string;
  enrichment_status: string;
  verification_status: string;
  severity: string;
  confidence_score: number;
  threat_types: string[];
  source: string;
  description?: string;
  enrichment_data: Record<string, any>;
  reputation_score?: number;
  last_enriched_at?: string;
  first_seen: string;
  last_seen: string;
  related_alert_count: number;
  tags: string[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  severity?: string;
  details: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship: string;
  confidence: number;
}

export interface MitreTechnique {
  id: number;
  technique_id: string;
  name: string;
  tactic: string;
  description?: string;
  attack_categories: string[];
  mapping_rationale?: string;
  attck_version: string;
  confidence_weight: number;
  url?: string;
}

export interface FederatedClient {
  id: number;
  client_id: string;
  name: string;
  organization: string;
  industry_sector: string;
  dataset_name: string;
  local_sample_count: number;
  status: string;
  current_round: number;
  local_accuracy?: number;
  local_loss?: number;
  last_heartbeat: string;
}

export interface FederatedRound {
  id: number;
  round_number: number;
  status: string;
  aggregation_strategy: string;
  participating_clients: string[];
  total_samples: number;
  global_accuracy_before?: number;
  global_accuracy_after?: number;
  global_loss_before?: number;
  global_loss_after?: number;
  client_metrics: Record<string, any>;
  created_at: string;
}

export interface BigFlowCategoryItem {
  name: string;
  group: string;
  is_attack: boolean;
  is_supported: boolean;
  partition_file: string;
  unsupported_reason?: string | null;
}

export interface BigFlowCategoriesResponse {
  status: string;
  total_categories: number;
  active_model_name?: string | null;
  model_supported_count: number;
  unsupported_count: number;
  categories: BigFlowCategoryItem[];
}

export interface BigFlowReplayRequest {
  category: string;
  batch_size: number;
  create_alerts?: boolean;
}

export interface BigFlowReplayItem {
  flow_id: string;
  timestamp: string;
  src_ip: string;
  dst_ip: string;
  src_port: number;
  dst_port: number;
  protocol: string;
  ground_truth_attack: string;
  ground_truth_label: number;
  is_ground_truth_malicious: boolean;
  predicted_class: string;
  confidence: number;
  is_malicious: boolean;
  model_version: string;
  model_supported: boolean;
  is_correct_prediction: boolean;
  unsupported_warning?: string | null;
  risk_score: number;
  severity: string;
  inference_time_ms: number;
  feature_importances: FeatureImportanceItem[];
  human_explanation?: string;
  dataset_source: string;
  alert_created: boolean;
  ingestion_source?: string;
  is_anomaly?: boolean;
}

export interface BigFlowReplayResponse {
  category_requested: string;
  processed_count: number;
  malicious_count: number;
  benign_count: number;
  accuracy_on_supported?: number | null;
  items: BigFlowReplayItem[];
}
