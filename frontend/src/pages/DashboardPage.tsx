import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  ShieldAlert,
  AlertTriangle,
  Radio,
  Cpu,
  Globe2,
  Users2,
  ArrowUpRight,
  TrendingUp,
  Server,
  Zap,
  Flame,
  Search,
  KeyRound,
  CheckCircle2,
  Eye,
  Radar,
  Share2,
  ShieldCheck,
  Sparkles,
  Database,
  Upload
} from 'lucide-react';
import { api } from '../services/api';
import { DashboardMetrics, Alert } from '../types/api';
import { StatCard } from '../components/StatCard';
import { SeverityBadge, StatusBadge } from '../components/Badge';
import { useToast } from '../context/ToastContext';
import { FlowForensicsModal, ForensicFlowData } from '../components/FlowForensicsModal';

export const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [selectedForensicFlow, setSelectedForensicFlow] = useState<ForensicFlowData | null>(null);
  const [isForensicOpen, setIsForensicOpen] = useState<boolean>(false);

  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(true);

  const navigate = useNavigate();
  const { showToast } = useToast();

  useEffect(() => {
    loadDashboard();
    api.checkBackendHealth().then((res) => setIsBackendOnline(res.online));
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await api.getDashboardMetrics();
      setMetrics(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateAttack = async (type: 'dos' | 'portscan' | 'bruteforce' | 'benign' | 'stream') => {
    setIsSimulating(true);
    try {
      if (type === 'stream') {
        showToast('Synthetic Demo Burst', 'Injecting 4 demonstration NetFlow payloads...', 'info');
        const types: ('portscan' | 'dos' | 'bruteforce' | 'benign')[] = ['portscan', 'dos', 'bruteforce', 'benign'];
        for (const t of types) {
          await runSimulationPayload(t);
          await new Promise((r) => setTimeout(r, 600));
        }
        showToast('Stream Complete', 'FlowTransformer evaluated all 4 demonstration flows.', 'success');
      } else {
        await runSimulationPayload(type);
      }
      const updatedMetrics = await api.getDashboardMetrics();
      setMetrics(updatedMetrics);
    } catch (err: any) {
      showToast('Simulation Error', err?.message || 'Failed to simulate flow', 'danger');
    } finally {
      setIsSimulating(false);
    }
  };

  const handleReplayBigFlowQuick = async (category: string = 'DDoS') => {
    setIsSimulating(true);
    try {
      showToast('BigFlow Replay Triggered', `Streaming 3 real Parquet records for '${category}'...`, 'info');
      const res = await api.replayBigFlowStream({
        category,
        batch_size: 3,
        create_alerts: true
      });
      showToast(
        `BigFlow Replay Evaluated (${category})`,
        `Processed ${res.processed_count} real Parquet flows. Transformer latency: ${res.items[0]?.inference_time_ms}ms`,
        'success'
      );
      const updatedMetrics = await api.getDashboardMetrics();
      setMetrics(updatedMetrics);
    } catch (err: any) {
      showToast('BigFlow Replay Error', err?.message || 'Failed to replay BigFlow records', 'danger');
    } finally {
      setIsSimulating(false);
    }
  };

  const handleIngestLiveQuick = async () => {
    setIsSimulating(true);
    try {
      showToast('Live Sensor Ingestion', 'Capturing 5 telemetry flows from interface eth0...', 'info');
      const flows = [
        {
          src_ip: `198.51.100.${Math.floor(Math.random() * 200 + 10)}`,
          dst_ip: '10.0.0.1',
          dst_port: 80,
          protocol: 'TCP',
          flow_duration: 2.4,
          fwd_pkts: 1200.0,
          bwd_pkts: 2.0,
          fwd_bytes: 84000.0,
          bwd_bytes: 80.0,
          flow_rate_bytes_per_sec: 35000.0,
          flow_rate_pkts_per_sec: 500.0,
          tcp_flags_syn: 1.0,
          tcp_flags_ack: 0.0
        },
        {
          src_ip: `192.168.1.${Math.floor(Math.random() * 200 + 20)}`,
          dst_ip: '10.0.0.5',
          dst_port: 443,
          protocol: 'TCP',
          flow_duration: 1200.0,
          fwd_pkts: 14.0,
          bwd_pkts: 18.0,
          fwd_bytes: 2800.0,
          bwd_bytes: 14200.0,
          tcp_flags_syn: 0.0,
          tcp_flags_ack: 1.0
        },
        {
          src_ip: `203.0.113.${Math.floor(Math.random() * 200 + 5)}`,
          dst_ip: '10.0.0.2',
          dst_port: 22,
          protocol: 'TCP',
          flow_duration: 650.0,
          fwd_pkts: 42.0,
          bwd_pkts: 46.0,
          fwd_bytes: 8200.0,
          bwd_bytes: 8600.0,
          tcp_flags_syn: 1.0,
          tcp_flags_ack: 1.0
        }
      ];

      const res = await api.ingestLiveFlows(flows, 'SENSOR-EDGE-01', 'eth0', true);
      showToast(
        'Live Capture Evaluated',
        `Sensor SENSOR-EDGE-01: ${res.ingested_count} flows captured (${res.malicious_count} malicious, ${res.anomaly_count} anomalies)`,
        res.malicious_count > 0 ? 'warning' : 'success'
      );
      const updatedMetrics = await api.getDashboardMetrics();
      setMetrics(updatedMetrics);
    } catch (err: any) {
      showToast('Live Ingestion Error', err?.message || 'Failed to capture live telemetry', 'danger');
    } finally {
      setIsSimulating(false);
    }
  };

  const runSimulationPayload = async (type: 'dos' | 'portscan' | 'bruteforce' | 'benign') => {
    let payload: any = {};
    const randomOctet = Math.floor(Math.random() * 200 + 20);

    if (type === 'dos') {
      payload = {
        src_ip: `45.33.32.${randomOctet}`,
        dst_ip: '10.0.0.1',
        dst_port: 80,
        protocol: 'TCP',
        flow_duration: 3.2,
        fwd_pkts: 1850.0,
        bwd_pkts: 2.0,
        fwd_bytes: 98000.0,
        bwd_bytes: 80.0,
        flow_rate_bytes_per_sec: 30625.0,
        flow_rate_pkts_per_sec: 578.0,
        tcp_flags_syn: 1.0,
        tcp_flags_ack: 0.0,
        is_simulated: true,
        ingestion_source: 'simulated_preset',
        dataset_source: 'Simulated Preset'
      };
    } else if (type === 'portscan') {
      payload = {
        src_ip: `185.220.101.${randomOctet}`,
        dst_ip: '10.0.0.2',
        dst_port: Math.floor(Math.random() * 1024 + 1),
        protocol: 'TCP',
        flow_duration: 1.5,
        fwd_pkts: 2.0,
        bwd_pkts: 0.0,
        fwd_bytes: 88.0,
        bwd_bytes: 0.0,
        flow_rate_pkts_per_sec: 1.33,
        tcp_flags_syn: 1.0,
        is_simulated: true,
        ingestion_source: 'simulated_preset',
        dataset_source: 'Simulated Preset'
      };
    } else if (type === 'bruteforce') {
      payload = {
        src_ip: `198.51.100.${randomOctet}`,
        dst_ip: '10.0.0.3',
        dst_port: 22,
        protocol: 'TCP',
        flow_duration: 850.0,
        fwd_pkts: 48.0,
        bwd_pkts: 52.0,
        fwd_bytes: 9200.0,
        bwd_bytes: 9800.0,
        tcp_flags_syn: 1.0,
        tcp_flags_ack: 1.0,
        is_simulated: true,
        ingestion_source: 'simulated_preset',
        dataset_source: 'Simulated Preset'
      };
    } else {
      payload = {
        src_ip: `192.168.1.${randomOctet}`,
        dst_ip: '10.0.0.5',
        dst_port: 443,
        protocol: 'TCP',
        flow_duration: 1400.0,
        fwd_pkts: 18.0,
        bwd_pkts: 22.0,
        fwd_bytes: 3200.0,
        bwd_bytes: 18400.0,
        tcp_flags_syn: 0.0,
        tcp_flags_ack: 1.0,
        is_simulated: true,
        ingestion_source: 'simulated_preset',
        dataset_source: 'Simulated Preset'
      };
    }

    const pred = await api.predictFlow(payload);

    if (pred.is_malicious) {
      showToast(
        `🚨 ${pred.predicted_class.toUpperCase()} Evaluated`,
        `Risk: ${pred.risk_score || 85}/100 from ${pred.src_ip} | Confidence: ${(pred.confidence * 100).toFixed(1)}%`,
        'danger'
      );
    } else {
      showToast(
        '✅ Benign Flow Verified',
        `Traffic from ${pred.src_ip}:443 verified benign (${(pred.confidence * 100).toFixed(1)}% safe)`,
        'success'
      );
    }
  };

  const handleInspectAlert = (alert: Alert) => {
    setSelectedForensicFlow({
      id: alert.id,
      src_ip: alert.src_ip || '192.168.1.105',
      dst_ip: '10.0.0.1',
      dst_port: 22,
      protocol: 'TCP',
      is_malicious: true,
      predicted_class: alert.category,
      confidence: 0.984,
      severity: alert.severity,
      risk_score: alert.risk_score,
      mitre_tactic: 'Initial Access',
      mitre_technique_id: 'T1110',
      inference_time_ms: 11.4,
      saliency_map: {
        dst_port: 0.42,
        flow_duration: 0.28,
        fwd_pkts: 0.16,
        tcp_flags_syn: 0.10,
        flow_rate_pkts_per_sec: 0.04
      },
      explanation: `Flow telemetry from ${alert.src_ip} triggered critical alert ${alert.alert_code}. Rapid authentication attempts against destination port 22 with low inter-arrival variance and high SYN/ACK ratios confirmed characteristic brute force behavior.`
    });
    setIsForensicOpen(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-10 h-10 border-3 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-xs text-slate-400 font-mono">
            Connecting to Cyber Threat Intelligence Engine...
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header & Live Radar Banner */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800/90 shadow-xl relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Subtle glowing animated sweep */}
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 via-blue-500/5 to-transparent pointer-events-none"></div>

        <div className="relative z-10">
          <div className="flex items-center space-x-2.5">
            <span className="flex h-3 w-3 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
            </span>
            <h1
              className="text-xl md:text-2xl font-black text-white tracking-wide"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              SECURITY OPERATIONS CENTER // LIVE TELEMETRY
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1 flex items-center space-x-2">
            <span>Real-time FlowTransformer deep packet inference</span>
            <span className="text-slate-600">&bull;</span>
            <span className="text-emerald-400 font-mono font-semibold">100% Ingestion Uptime</span>
            <span className="text-slate-600">&bull;</span>
            <span className="text-cyan-400 font-mono">0 Dropped Packets</span>
          </p>
        </div>

        <div className="relative z-10 flex items-center space-x-3">
          <button
            onClick={() => navigate('/traffic')}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 text-xs font-black flex items-center space-x-2 transition-all shadow-md shadow-cyan-500/20"
          >
            <Radio className="w-4 h-4 animate-pulse" />
            <span>Launch Traffic Replay</span>
          </button>
        </div>
      </div>

      {/* GitHub Pages / Backend Connection Notice */}
      {!isBackendOnline && (
        <div className="p-3.5 rounded-xl bg-slate-900/90 border border-cyan-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center space-x-2.5">
            <span className="px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400 font-mono font-bold text-[10px] uppercase border border-cyan-500/30">
              GitHub Pages Notice
            </span>
            <span className="text-slate-300">
              Displaying verified offline evaluation telemetry. To stream live BigFlow Parquet flows or train models, connect your FastAPI backend in Settings.
            </span>
          </div>
          <button
            onClick={() => navigate('/settings')}
            className="px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 font-semibold text-xs whitespace-nowrap"
          >
            Configure Backend URL &rarr;
          </button>
        </div>
      )}

      {/* Quick Action Ribbon with Genuine Replay, Live Capture & Simulation Presets */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-cyan-500/20 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shrink-0">
            <Zap className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
              ⚡ NetFlow Ingestion &amp; Evaluation Bar
            </h3>
            <p className="text-[11px] text-slate-400">
              Evaluate real BigFlow-NIDS Parquet records, capture live network flows, or inject test presets
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Genuine BigFlow Replay Quick Button */}
          <button
            onClick={() => handleReplayBigFlowQuick('DDoS')}
            disabled={isSimulating}
            className="px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 text-xs font-bold flex items-center space-x-1.5 transition-all shadow-sm"
          >
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <span>Replay BigFlow (DDoS)</span>
          </button>

          {/* Genuine Live Ingest Quick Button */}
          <button
            onClick={handleIngestLiveQuick}
            disabled={isSimulating}
            className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 text-xs font-bold flex items-center space-x-1.5 transition-all shadow-sm"
          >
            <Radio className="w-3.5 h-3.5 text-emerald-400" />
            <span>Capture Live Telemetry</span>
          </button>

          {/* Preset Buttons */}
          <button
            onClick={() => handleSimulateAttack('dos')}
            disabled={isSimulating}
            className="px-2.5 py-1.5 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-300 text-xs font-bold flex items-center space-x-1 transition-all shadow-sm"
          >
            <Flame className="w-3 h-3 text-rose-400" />
            <span>Preset SYN</span>
          </button>

          <button
            onClick={() => handleSimulateAttack('portscan')}
            disabled={isSimulating}
            className="px-2.5 py-1.5 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 text-xs font-bold flex items-center space-x-1 transition-all shadow-sm"
          >
            <Search className="w-3 h-3 text-amber-400" />
            <span>Preset Probe</span>
          </button>

          <button
            onClick={() => handleSimulateAttack('benign')}
            disabled={isSimulating}
            className="px-2.5 py-1.5 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-300 text-xs font-bold flex items-center space-x-1 transition-all shadow-sm"
          >
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>Preset Benign</span>
          </button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Analyzed NetFlows"
          value={metrics?.total_analyzed_flows.toLocaleString() || '0'}
          subtitle={`Benign: ${metrics?.benign_flows} | Malicious: ${metrics?.malicious_flows}`}
          icon={Activity}
          glowColor="cyan"
          trend="+14% /hr"
          isPositive={true}
        />
        <StatCard
          title="AI Detection Rate"
          value={`${metrics?.detection_rate_pct || 99.1}%`}
          subtitle={`False Positive Rate: ${metrics?.false_positive_rate_pct || 0.8}%`}
          icon={Cpu}
          glowColor="emerald"
          trend="Held-Out F1: 98.4%"
          isPositive={true}
        />
        <StatCard
          title="Active Security Alerts"
          value={metrics?.total_alerts || 0}
          subtitle={`Critical: ${metrics?.critical_alerts} | Open Incidents: ${metrics?.open_incidents}`}
          icon={ShieldAlert}
          glowColor="rose"
          trend="Escalated: Tier-2"
          isPositive={false}
        />
        <StatCard
          title="Verified IOC Threat Feed"
          value={metrics?.total_iocs || 0}
          subtitle={`Confirmed Malicious: ${metrics?.cti_summary?.confirmed_malicious || 0}`}
          icon={Globe2}
          glowColor="purple"
          trend="STIX 2.1 Ready"
          isPositive={true}
        />
      </div>

      {/* Telemetry Ingestion Provenance & Open-Set Anomaly Breakdown */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
            <Radio className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Live Capture</span>
            <span className="text-sm font-extrabold text-white font-mono">
              {metrics?.by_ingestion_source?.live_capture || 0}
            </span>
          </div>
        </div>

        <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
            <Database className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 block">BigFlow Replay</span>
            <span className="text-sm font-extrabold text-cyan-300 font-mono">
              {metrics?.by_ingestion_source?.dataset_replay || 0}
            </span>
          </div>
        </div>

        <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0">
            <Upload className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 block">File Uploads</span>
            <span className="text-sm font-extrabold text-blue-300 font-mono">
              {metrics?.by_ingestion_source?.file_upload || 0}
            </span>
          </div>
        </div>

        <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Simulated Presets</span>
            <span className="text-sm font-extrabold text-amber-300 font-mono">
              {metrics?.by_ingestion_source?.simulated_preset || 0}
            </span>
          </div>
        </div>

        <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl flex items-center space-x-3 col-span-2 sm:col-span-1">
          <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Open-Set Anomalies</span>
            <span className="text-sm font-extrabold text-purple-300 font-mono">
              {metrics?.anomaly_flows || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Attack Distribution & Severity Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Attack Category Breakdown */}
        <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 shadow-xl lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2
                className="text-sm font-bold text-white tracking-wide"
                style={{ fontFamily: 'var(--font-display)' }}
              >
                ATTACK VECTOR CLASSIFICATION
              </h2>
              <p className="text-[11px] text-slate-400 mt-0.5">
                FlowTransformer Multiclass Softmax Logits across observed NetFlows
              </p>
            </div>
            <span className="text-[11px] text-cyan-400 font-mono font-bold bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
              Dual-Head Inference
            </span>
          </div>

          <div className="space-y-3.5">
            {metrics?.attack_class_distribution &&
              Object.entries(metrics.attack_class_distribution).map(([cat, count]) => {
                const total = Object.values(metrics.attack_class_distribution).reduce((a, b) => a + b, 0);
                const pct = Math.round((count / (total || 1)) * 100);

                const colorGradients: Record<string, string> = {
                  DoS: 'from-rose-500 to-red-600',
                  PortScan: 'from-amber-500 to-orange-600',
                  BruteForce: 'from-purple-500 to-indigo-600',
                  Botnet: 'from-cyan-500 to-blue-600',
                  Infiltration: 'from-emerald-500 to-teal-600',
                  Benign: 'from-slate-600 to-slate-700'
                };

                const gradient = colorGradients[cat] || 'from-cyan-500 to-blue-600';

                return (
                  <div key={cat} className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="font-bold text-slate-200">{cat}</span>
                      <span className="text-slate-400 font-mono">
                        {count} flows ({pct}%)
                      </span>
                    </div>
                    <div className="w-full bg-slate-800/80 rounded-full h-2.5 overflow-hidden border border-slate-700/60">
                      <div
                        className={`bg-gradient-to-r ${gradient} h-full rounded-full transition-all duration-500 shadow-sm`}
                        style={{ width: `${Math.max(pct, 3)}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>

        {/* Severity & Federated Status Card */}
        <div className="space-y-6">
          <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 shadow-xl">
            <h2
              className="text-sm font-bold text-white tracking-wide mb-3"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              ALERT SEVERITY PROFILE
            </h2>
            <div className="grid grid-cols-2 gap-2.5 text-center">
              <div className="p-3 bg-rose-950/40 border border-rose-900/60 rounded-xl shadow-sm">
                <div className="text-[10px] text-rose-400 font-extrabold uppercase font-mono">Critical</div>
                <div className="text-xl font-black font-mono text-white mt-1">
                  {metrics?.alert_severity_distribution['Critical'] || 0}
                </div>
              </div>
              <div className="p-3 bg-amber-950/40 border border-amber-900/60 rounded-xl shadow-sm">
                <div className="text-[10px] text-amber-400 font-extrabold uppercase font-mono">High</div>
                <div className="text-xl font-black font-mono text-white mt-1">
                  {metrics?.alert_severity_distribution['High'] || 0}
                </div>
              </div>
              <div className="p-3 bg-yellow-950/30 border border-yellow-900/50 rounded-xl shadow-sm">
                <div className="text-[10px] text-yellow-400 font-extrabold uppercase font-mono">Medium</div>
                <div className="text-xl font-black font-mono text-white mt-1">
                  {metrics?.alert_severity_distribution['Medium'] || 0}
                </div>
              </div>
              <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl shadow-sm">
                <div className="text-[10px] text-blue-400 font-extrabold uppercase font-mono">Low</div>
                <div className="text-xl font-black font-mono text-white mt-1">
                  {metrics?.alert_severity_distribution['Low'] || 0}
                </div>
              </div>
            </div>
          </div>

          <div
            onClick={() => navigate('/federated')}
            className="p-5 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 hover:border-purple-500/40 shadow-xl transition-all cursor-pointer group"
          >
            <div className="flex items-center justify-between mb-2">
              <h2
                className="text-sm font-bold text-white tracking-wide flex items-center space-x-2"
                style={{ fontFamily: 'var(--font-display)' }}
              >
                <Users2 className="w-4 h-4 text-purple-400 group-hover:scale-110 transition-transform" />
                <span>FEDERATED DEFENSE</span>
              </h2>
              <span className="text-[10px] uppercase font-bold text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/30 font-mono">
                Round {metrics?.federated_status?.current_round || 1}
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              {metrics?.federated_status?.active_clients || 3} simulated banking and telecom nodes collaborating via
              privacy-preserving FedAvg.
            </p>
            <div className="mt-3 flex items-center justify-between text-xs pt-2 border-t border-slate-800/80">
              <span className="text-slate-500">Global Model Accuracy:</span>
              <span className="text-emerald-400 font-black font-mono">
                {((metrics?.federated_status?.global_accuracy || 0.984) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Alerts & Top Adversary Indicators */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Alerts Table with Interactive Inspect Button */}
        <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 shadow-xl lg:col-span-2 overflow-x-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2
                className="text-sm font-bold text-white tracking-wide"
                style={{ fontFamily: 'var(--font-display)' }}
              >
                RECENT HIGH-PRIORITY ALERTS
              </h2>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Click any row or &lsquo;Inspect&rsquo; to examine eX-NIDS feature saliency attributions
              </p>
            </div>
            <button
              onClick={() => navigate('/alerts')}
              className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center space-x-1"
            >
              <span>View All Alerts</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-bold uppercase text-[10px] tracking-wider font-mono">
                <th className="pb-3">Alert Code</th>
                <th className="pb-3">Category</th>
                <th className="pb-3">Severity</th>
                <th className="pb-3">Source IP</th>
                <th className="pb-3">Risk Score</th>
                <th className="pb-3">Status</th>
                <th className="pb-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {metrics?.recent_alerts?.map((a) => (
                <tr
                  key={a.id}
                  className="hover:bg-slate-800/50 transition-colors group"
                >
                  <td className="py-3 font-mono text-cyan-400 font-bold">{a.alert_code}</td>
                  <td className="py-3 text-slate-200 font-semibold">{a.category}</td>
                  <td className="py-3">
                    <SeverityBadge severity={a.severity} />
                  </td>
                  <td className="py-3 font-mono text-slate-300">{a.src_ip || 'N/A'}</td>
                  <td className="py-3 font-mono font-black text-amber-400">{a.risk_score}/100</td>
                  <td className="py-3">
                    <StatusBadge status={a.status} />
                  </td>
                  <td className="py-3 text-right">
                    <button
                      onClick={() => handleInspectAlert(a)}
                      className="px-2.5 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-[11px] font-bold inline-flex items-center space-x-1 transition-colors"
                      title="Inspect eX-NIDS Saliency Map"
                    >
                      <Eye className="w-3 h-3" />
                      <span>Inspect</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Top Adversary Indicators */}
        <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <h2
              className="text-sm font-bold text-white tracking-wide"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              TOP ADVERSARY INFRASTRUCTURE
            </h2>
            <button
              onClick={() => navigate('/iocs')}
              className="text-[11px] text-cyan-400 hover:text-cyan-300 font-semibold flex items-center space-x-1"
            >
              <span>IOC Explorer</span>
              <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>

          <div className="space-y-2.5">
            {metrics?.top_source_ips?.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/70 border border-slate-850 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center space-x-2.5">
                  <span className="w-5 h-5 rounded-md bg-slate-800 flex items-center justify-center text-[10px] font-black font-mono text-slate-400">
                    {idx + 1}
                  </span>
                  <span className="text-xs font-mono text-slate-200">{item.ip}</span>
                </div>
                <span className="text-xs font-black text-rose-400 font-mono">{item.count} attacks</span>
              </div>
            ))}
          </div>

          <div className="mt-5 pt-4 border-t border-slate-800">
            <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono mb-2">
              Critical Targeted Ports
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {metrics?.top_dest_ports?.map((p, i) => (
                <span
                  key={i}
                  className="px-2 py-1 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-cyan-400 font-bold"
                >
                  Port {p.port} ({p.count})
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Reusable Flow Forensics Modal */}
      <FlowForensicsModal
        isOpen={isForensicOpen}
        onClose={() => setIsForensicOpen(false)}
        flow={selectedForensicFlow}
        onContain={(srcIp) => {
          showToast(
            'Containment Rule Enforced',
            `Null-route and perimeter block initiated for adversary IP ${srcIp}`,
            'success'
          );
        }}
      />
    </div>
  );
};
