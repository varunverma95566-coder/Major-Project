import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  X,
  Shield,
  Activity,
  Cpu,
  Share2,
  Users2,
  FileText,
  Sparkles,
  ArrowRight,
  Database,
  Search
} from 'lucide-react';

interface QuickTourModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const QuickTourModal: React.FC<QuickTourModalProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();

  if (!isOpen) return null;

  const tourFeatures = [
    {
      title: '1. Live Traffic & Replay Stream',
      icon: Activity,
      desc: 'Simulate or stream real-time NetFlow v5/v9 & IPFIX packets. Test attack vectors (DoS, PortScan, SSH BruteForce) and observe live line-rate inference.',
      path: '/traffic',
      badge: 'Interactive Simulator'
    },
    {
      title: '2. FlowTransformer & eX-NIDS Forensics',
      icon: Cpu,
      desc: 'Inspect deep 42-feature packet breakdowns, self-attention representations, and Input x Gradient saliency attributions that explain why an attack was classified.',
      path: '/investigation',
      badge: 'Explainable AI'
    },
    {
      title: '3. Security Alerts & Multi-Factor Risk',
      icon: Shield,
      desc: 'Triage live detections rated on a calibrated 0–100 multi-factor risk score combining neural confidence, port criticality, and CTI reputation.',
      path: '/alerts',
      badge: 'SOC Triage'
    },
    {
      title: '4. Threat Correlation & Knowledge Graph',
      icon: Share2,
      desc: 'Explore interactive node-link graphs clustering attacker IPs, victim hosts, targeted ports, and MITRE ATT&CK techniques into unified incident campaigns.',
      path: '/graph',
      badge: 'Visual Analytics'
    },
    {
      title: '5. Collaborative Federated Defense (FedAvg)',
      icon: Users2,
      desc: 'Simulate multi-organization collaborative learning across FinBank, MedHealth, and CloudTel, aggregating model weights without sharing private flow payloads.',
      path: '/federated',
      badge: 'Privacy-Preserving'
    },
    {
      title: '6. CTI, IOC Database & STIX 2.1 Export',
      icon: FileText,
      desc: 'Search Indicators of Compromise (IPs, hashes, domains) enriched via AbuseIPDB/VirusTotal, and export OASIS STIX 2.1 bundles ready for TAXII.',
      path: '/iocs',
      badge: 'STIX 2.1 Standard'
    }
  ];

  const handleNavigate = (path: string) => {
    onClose();
    navigate(path);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-6 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white tracking-wide flex items-center gap-2">
                <span>Cyber-Sentinel SOC Platform Guide</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                  Quick Tour
                </span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Understand how the Transformer NIDS, eX-NIDS explainability, and CTI engine operate
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

        {/* Modal Body / Feature Cards */}
        <div className="p-6 overflow-y-auto space-y-3.5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {tourFeatures.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <div
                  key={idx}
                  onClick={() => handleNavigate(feat.path)}
                  className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-cyan-500/40 hover:bg-slate-850/80 transition-all duration-200 cursor-pointer group flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <div className="w-7 h-7 rounded-lg bg-slate-900 border border-slate-700 flex items-center justify-center text-cyan-400 group-hover:scale-110 transition-transform">
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <h4 className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors">
                          {feat.title}
                        </h4>
                      </div>
                      <span className="text-[9px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        {feat.badge}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 leading-relaxed mb-3">
                      {feat.desc}
                    </p>
                  </div>
                  <div className="flex items-center text-[10px] font-semibold text-cyan-400 group-hover:translate-x-1 transition-transform">
                    <span>Open Section</span>
                    <ArrowRight className="w-3 h-3 ml-1" />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-slate-950 border-t border-slate-800 flex items-center justify-between">
          <span className="text-[11px] text-slate-400 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            All 14 modules are live and connected to the local development engine
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-colors shadow-sm shadow-cyan-500/20"
          >
            Start Exploring
          </button>
        </div>
      </div>
    </div>
  );
};
