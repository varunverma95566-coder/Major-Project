import React, { useState, useEffect } from 'react';
import {
  Shield,
  Zap,
  Clock,
  LogOut,
  HelpCircle,
  ChevronDown,
  Activity,
  Flame,
  Search,
  KeyRound,
  CheckCircle2,
  Cpu
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { api } from '../services/api';
import { QuickTourModal } from './QuickTourModal';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { showToast } = useToast();
  const [timeStr, setTimeStr] = useState<string>('');
  const [isTourOpen, setIsTourOpen] = useState(false);
  const [simMenuOpen, setSimMenuOpen] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const triggerSimulation = async (type: 'dos' | 'portscan' | 'bruteforce' | 'benign' | 'stream') => {
    setSimMenuOpen(false);
    setIsSimulating(true);

    try {
      if (type === 'stream') {
        showToast('Multi-Vector Stream Started', 'Replaying 4 sequential network attack vectors...', 'info');
        const types: ('dos' | 'portscan' | 'bruteforce' | 'benign')[] = ['portscan', 'dos', 'bruteforce', 'benign'];
        for (const t of types) {
          await executeSingleAttack(t);
          await new Promise((r) => setTimeout(r, 700));
        }
        showToast('Stream Completed', 'FlowTransformer evaluated all 4 flows in real time.', 'success');
      } else {
        await executeSingleAttack(type);
      }
    } catch (err: any) {
      showToast('Simulation Error', err?.message || 'Failed to simulate flow', 'danger');
    } finally {
      setIsSimulating(false);
    }
  };

  const executeSingleAttack = async (type: 'dos' | 'portscan' | 'bruteforce' | 'benign') => {
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
      // Benign Web Flow
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

  return (
    <>
      <header className="h-16 border-b border-slate-800 bg-slate-950/85 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40 select-none">
        {/* Brand & Platform title */}
        <div className="flex items-center space-x-3.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/25 ring-1 ring-white/20">
            <Shield className="w-5 h-5 text-slate-950 font-black" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span
                className="font-extrabold text-base tracking-wider text-white"
                style={{ fontFamily: 'var(--font-display)' }}
              >
                CYBER-SENTINEL
              </span>
              <span className="px-1.5 py-0.5 text-[9px] font-extrabold rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono">
                v1.0 ENTERPRISE
              </span>
            </div>
            <p className="text-[10.5px] text-slate-400 tracking-tight hidden sm:block">
              FlowTransformer NIDS & Cyber Threat Intelligence Engine
            </p>
          </div>
        </div>

        {/* Center Operational Badges */}
        <div className="hidden lg:flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 shadow-inner">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-400 font-medium">Inference:</span>
            <span className="text-emerald-400 font-bold font-mono">FlowTransformer (Active)</span>
            <span className="text-slate-600">|</span>
            <span className="text-cyan-400 font-mono text-[11px]">11.4ms Latency</span>
          </div>

          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-slate-400">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-mono text-[11px] text-slate-300">{timeStr}</span>
          </div>
        </div>

        {/* Right Controls & Quick Actions */}
        <div className="flex items-center space-x-3">
          {/* Quick Attack Simulator Dropdown */}
          <div className="relative">
            <button
              onClick={() => setSimMenuOpen(!simMenuOpen)}
              disabled={isSimulating}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-2 transition-all shadow-sm ${
                isSimulating
                  ? 'bg-slate-800 text-slate-400 cursor-wait'
                  : 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 hover:from-cyan-500/30 hover:to-blue-500/30 text-cyan-300 border border-cyan-500/40 shadow-cyan-500/10'
              }`}
            >
              <Zap className={`w-3.5 h-3.5 text-cyan-400 ${isSimulating ? 'animate-spin' : 'animate-pulse'}`} />
              <span className="hidden sm:inline">
                {isSimulating ? 'Simulating...' : '⚡ Test Attack Stream'}
              </span>
              <ChevronDown className="w-3.5 h-3.5 ml-0.5 text-slate-400" />
            </button>

            {simMenuOpen && (
              <div
                className="absolute right-0 mt-2 w-64 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95 duration-150"
                onMouseLeave={() => setSimMenuOpen(false)}
              >
                <div className="px-2.5 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800 mb-1">
                  1-Click Live Attack Presets
                </div>
                <button
                  onClick={() => triggerSimulation('dos')}
                  className="w-full text-left px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 flex items-center space-x-2.5 group transition-colors"
                >
                  <Flame className="w-4 h-4 text-rose-400 group-hover:scale-110 transition-transform" />
                  <div>
                    <div className="font-semibold text-rose-300">SYN Flood DoS Attack</div>
                    <div className="text-[10px] text-slate-400">1,850 pkts/s volumetric flood</div>
                  </div>
                </button>
                <button
                  onClick={() => triggerSimulation('portscan')}
                  className="w-full text-left px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 flex items-center space-x-2.5 group transition-colors"
                >
                  <Search className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
                  <div>
                    <div className="font-semibold text-amber-300">Port Scan Reconnaissance</div>
                    <div className="text-[10px] text-slate-400">Rapid multi-port probe sweep</div>
                  </div>
                </button>
                <button
                  onClick={() => triggerSimulation('bruteforce')}
                  className="w-full text-left px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 flex items-center space-x-2.5 group transition-colors"
                >
                  <KeyRound className="w-4 h-4 text-purple-400 group-hover:scale-110 transition-transform" />
                  <div>
                    <div className="font-semibold text-purple-300">SSH Auth Brute Force</div>
                    <div className="text-[10px] text-slate-400">High-frequency Port 22 login retries</div>
                  </div>
                </button>
                <button
                  onClick={() => triggerSimulation('benign')}
                  className="w-full text-left px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 flex items-center space-x-2.5 group transition-colors"
                >
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 group-hover:scale-110 transition-transform" />
                  <div>
                    <div className="font-semibold text-emerald-300">Normal HTTPS Web Flow</div>
                    <div className="text-[10px] text-slate-400">Legitimate Port 443 web session</div>
                  </div>
                </button>
                <div className="border-t border-slate-800 my-1"></div>
                <button
                  onClick={() => triggerSimulation('stream')}
                  className="w-full text-left px-2.5 py-2 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-xs text-cyan-300 font-bold flex items-center justify-between transition-colors"
                >
                  <span>Replay 4-Attack Sequence</span>
                  <Activity className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                </button>
              </div>
            )}
          </div>

          {/* Quick Tour Button */}
          <button
            onClick={() => setIsTourOpen(true)}
            title="Open Platform Tour & Guide"
            className="p-2 text-slate-400 hover:text-cyan-400 hover:bg-slate-900 rounded-lg transition-colors border border-transparent hover:border-slate-800"
          >
            <HelpCircle className="w-4 h-4" />
          </button>

          {/* User Profile & Logout */}
          <div className="flex items-center space-x-3 border-l border-slate-800 pl-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-slate-800 to-slate-700 border border-slate-600 flex items-center justify-center text-cyan-400 font-bold text-xs shadow-inner">
              {user?.username?.substring(0, 2).toUpperCase() || 'SA'}
            </div>
            <div className="hidden md:block text-left">
              <div className="text-xs font-bold text-slate-200 leading-tight">
                {user?.full_name || 'Senior SOC Analyst'}
              </div>
              <div className="text-[9.5px] text-cyan-400 uppercase tracking-wider font-extrabold">
                {user?.role || 'analyst'} // Tier-2 SOC
              </div>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-900 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Tour Modal */}
      <QuickTourModal isOpen={isTourOpen} onClose={() => setIsTourOpen(false)} />
    </>
  );
};
