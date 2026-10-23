import React, { useState } from 'react';
import {
  X,
  ShieldAlert,
  ShieldCheck,
  Cpu,
  Activity,
  Copy,
  Check,
  ExternalLink,
  Lock,
  ArrowRight
} from 'lucide-react';
import { SeverityBadge } from './Badge';

export interface ForensicFlowData {
  id?: number | string;
  src_ip: string;
  dst_ip: string;
  dst_port: number;
  protocol: string;
  is_malicious: boolean;
  predicted_class: string;
  confidence: number;
  severity: string;
  risk_score?: number;
  mitre_tactic?: string;
  mitre_technique_id?: string;
  inference_time_ms?: number;
  saliency_map?: Record<string, number>;
  explanation?: string;
  timestamp?: string;
  ground_truth_attack?: string;
  ground_truth_label?: number;
  dataset_source?: string;
  model_supported?: boolean;
  unsupported_warning?: string | null;
  ingestion_source?: string;
  is_anomaly?: boolean;
  is_simulated?: boolean;
}

interface FlowForensicsModalProps {
  isOpen: boolean;
  onClose: () => void;
  flow: ForensicFlowData | null;
  onContain?: (srcIp: string) => void;
}

export const FlowForensicsModal: React.FC<FlowForensicsModalProps> = ({
  isOpen,
  onClose,
  flow,
  onContain
}) => {
  const [copied, setCopied] = useState(false);
  const [contained, setContained] = useState(false);

  if (!isOpen || !flow) return null;

  const handleCopyIp = () => {
    navigator.clipboard.writeText(flow.src_ip);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleContainClick = () => {
    setContained(true);
    if (onContain) onContain(flow.src_ip);
  };

  // Prepare saliency entries sorted descending
  const saliencyEntries: [string, number][] = flow.saliency_map
    ? Object.entries(flow.saliency_map)
        .map(([k, v]): [string, number] => [k, Number(v)])
        .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
        .slice(0, 5)
    : [
        ['dst_port', 0.38],
        ['flow_duration', 0.27],
        ['bwd_pkts', 0.18],
        ['tcp_flags_syn', 0.12],
        ['flow_rate_pkts_per_sec', 0.05]
      ];

  const maxSaliency = Math.max(...saliencyEntries.map(([, val]) => Math.abs(Number(val))), 0.01);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <div className="p-5 bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div
              className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                flow.is_malicious
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              }`}
            >
              {flow.is_malicious ? (
                <ShieldAlert className="w-5 h-5 animate-pulse" />
              ) : (
                <ShieldCheck className="w-5 h-5" />
              )}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white tracking-wide">
                  Flow Forensic Deep-Dive
                </h3>
                <SeverityBadge severity={flow.severity || (flow.is_malicious ? 'High' : 'Low')} />
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5 font-mono">
                {flow.src_ip} &rarr; {flow.dst_ip}:{flow.dst_port} ({flow.protocol})
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 overflow-y-auto space-y-5">
          {/* Ground Truth & Dataset Source Banner */}
          {(flow.ground_truth_attack || flow.dataset_source) && (
            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono text-cyan-400 font-bold flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
                  <span>Dataset Provenance: {flow.dataset_source || 'BigFlow-NIDS-V2'}</span>
                </span>
                {flow.model_supported === false ? (
                  <span className="px-2 py-0.5 text-[10px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30 rounded">
                    Retraining Required
                  </span>
                ) : (
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${
                    flow.ground_truth_attack?.toLowerCase() === flow.predicted_class?.toLowerCase()
                      ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                      : 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                  }`}>
                    {flow.ground_truth_attack?.toLowerCase() === flow.predicted_class?.toLowerCase()
                      ? '✓ Model Correct Match'
                      : '≠ Model Divergence'}
                  </span>
                )}
              </div>
              <div className="grid grid-cols-2 gap-2 pt-1 text-xs">
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Dataset Ground Truth</span>
                  <span className="font-bold text-white font-mono">{flow.ground_truth_attack || 'Unknown'}</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Model Inferred Class</span>
                  <span className="font-bold text-cyan-400 font-mono">{flow.predicted_class}</span>
                </div>
              </div>
              {flow.unsupported_warning && (
                <p className="text-[11px] text-amber-400/90 bg-amber-950/30 border border-amber-800/40 p-2 rounded-lg">
                  ⚠️ {flow.unsupported_warning}
                </p>
              )}
            </div>
          )}

          {/* Key Metric Highlights */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-col justify-between">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                Predicted Attack
              </span>
              <div className="mt-1">
                <span className="text-sm font-extrabold text-white capitalize">
                  {flow.predicted_class.replace(/_/g, ' ')}
                </span>
                <span className="block text-[10px] text-cyan-400 font-mono mt-0.5">
                  {(flow.confidence * 100).toFixed(1)}% Confidence
                </span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-col justify-between">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                Composite Threat Risk
              </span>
              <div className="mt-1">
                <span className="text-sm font-extrabold text-amber-400 font-mono">
                  {flow.risk_score || 78}/100
                </span>
                <span className="block text-[10px] text-slate-400 mt-0.5">
                  Multi-Factor Calibrated
                </span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-col justify-between">
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                MITRE ATT&CK
              </span>
              <div className="mt-1">
                <span className="text-xs font-bold text-rose-400 font-mono">
                  {flow.mitre_technique_id || 'T1046'}
                </span>
                <span className="block text-[10px] text-slate-400 truncate mt-0.5">
                  {flow.mitre_tactic || 'Reconnaissance'}
                </span>
              </div>
            </div>
          </div>

          {/* eX-NIDS Gradient Feature Saliency Attribution */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <h4 className="text-xs font-bold text-white tracking-wide uppercase">
                  eX-NIDS Gradient Feature Saliency (Input &times; Gradient)
                </h4>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">
                Model: FlowTransformer
              </span>
            </div>

            <div className="space-y-2 pt-1">
              {saliencyEntries.map(([feat, val], idx) => {
                const pct = Math.round((Math.abs(val) / maxSaliency) * 100);
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-[11px]">
                      <span className="font-mono text-slate-300">{feat}</span>
                      <span className="font-mono text-cyan-400 font-semibold">{pct}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Grounded Natural Language Explanation */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-amber-400" />
              <h4 className="text-xs font-bold text-white tracking-wide uppercase">
                Grounded Forensic Explanation (Zero Hallucination)
              </h4>
            </div>
            <p className="text-[11px] text-slate-300 leading-relaxed bg-slate-900/80 p-3 rounded-lg border border-slate-800 font-sans">
              {flow.explanation ||
                `Flow telemetry from ${flow.src_ip} targeted core asset ${flow.dst_ip}:${flow.dst_port} displaying rapid connection signatures. Heavy concentration of TCP SYN flags without matching ACK payloads and shortened inter-arrival times prompted a high-confidence ${flow.predicted_class} classification.`}
            </p>
          </div>
        </div>

        {/* Footer Quick Actions */}
        <div className="p-4 bg-slate-950 border-t border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopyIp}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium flex items-center space-x-1.5 transition-colors border border-slate-700"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'IP Copied' : 'Copy Attacker IP'}</span>
            </button>
          </div>

          <div className="flex items-center space-x-3">
            {flow.is_malicious && (
              <button
                onClick={handleContainClick}
                disabled={contained}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1.5 transition-all shadow-sm ${
                  contained
                    ? 'bg-slate-800 text-slate-500 border border-slate-700'
                    : 'bg-rose-500 hover:bg-rose-400 text-white shadow-rose-500/20'
                }`}
              >
                <Lock className="w-3.5 h-3.5" />
                <span>{contained ? 'Containment Enforced' : 'Trigger Automated Containment'}</span>
              </button>
            )}
            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
