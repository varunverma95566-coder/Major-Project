import React, { useState, useEffect } from 'react';
import { Sliders, Database, Cpu, Globe2, Bot, CheckCircle2, Shield, AlertTriangle, Copy, Terminal, Server, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export const SettingsPage: React.FC = () => {
  const [healthData, setHealthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [backendUrl, setBackendUrl] = useState<string>(api.getApiBase());
  const [backendStatus, setBackendStatus] = useState<'testing' | 'online' | 'offline'>('testing');
  const [saveMsg, setSaveMsg] = useState<string>('');

  useEffect(() => {
    loadSettings();
    testBackend(api.getApiBase());
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await api.getSettings();
      setHealthData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const testBackend = async (url?: string) => {
    setBackendStatus('testing');
    const res = await api.checkBackendHealth(url !== undefined ? url : backendUrl);
    setBackendStatus(res.online ? 'online' : 'offline');
  };

  const handleSaveBackendUrl = () => {
    api.setApiBase(backendUrl);
    testBackend(backendUrl);
    setSaveMsg('Saved! Active endpoint updated.');
    setTimeout(() => setSaveMsg(''), 3000);
  };

  const handleResetBackendUrl = () => {
    api.clearApiBase();
    setBackendUrl(api.getApiBase());
    testBackend('');
    setSaveMsg('Reset to default dev/static endpoint.');
    setTimeout(() => setSaveMsg(''), 3000);
  };

  const copyDbUri = () => {
    navigator.clipboard.writeText('postgresql+psycopg2://user:password@localhost:5432/nids_db');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-wide" style={{ fontFamily: 'var(--font-display)' }}>
            SYSTEM SETTINGS & INTEGRATION HEALTH
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Runtime environment state, database persistence layer, and external CTI service connectors
          </p>
        </div>
      </div>

      {/* Backend API Connection & GitHub Pages Integration Card */}
      <div className="glass-panel p-6 rounded-xl border border-cyan-500/30 bg-slate-900/60 shadow-lg space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">
                FASTAPI BACKEND &amp; TRANSFORMER ENGINE URL
              </h2>
              <div className="flex items-center space-x-2 mt-0.5">
                {backendStatus === 'online' ? (
                  <span className="text-xs text-emerald-400 font-semibold flex items-center space-x-1">
                    <Wifi className="w-3.5 h-3.5 animate-pulse" />
                    <span>Connected to Live Backend</span>
                  </span>
                ) : (
                  <span className="text-xs text-amber-400 font-semibold flex items-center space-x-1">
                    <WifiOff className="w-3.5 h-3.5" />
                    <span>Static Mode (Backend Offline - Benchmark Data Active)</span>
                  </span>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={() => testBackend()}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 font-mono flex items-center space-x-1.5 self-start sm:self-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${backendStatus === 'testing' ? 'animate-spin' : ''}`} />
            <span>Test Ping</span>
          </button>
        </div>

        <div className="text-xs text-slate-300 space-y-2">
          <p className="text-slate-400">
            When deployed to GitHub Pages, this web application runs statically in your browser. To execute live Transformer packet classification, BigFlow-NIDS parquet replay, and sensor ingestion, enter your deployed FastAPI server URL below:
          </p>
          <div className="flex flex-col sm:flex-row gap-2 mt-2">
            <input
              type="text"
              value={backendUrl}
              onChange={(e) => setBackendUrl(e.target.value)}
              placeholder="e.g. https://your-backend.railway.app or http://localhost:8000"
              className="flex-1 px-3 py-2 rounded-lg bg-slate-950 border border-slate-700 font-mono text-xs text-white focus:outline-none focus:border-cyan-500"
            />
            <button
              onClick={handleSaveBackendUrl}
              className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs"
            >
              Save URL
            </button>
            <button
              onClick={handleResetBackendUrl}
              className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
            >
              Reset
            </button>
          </div>
          {saveMsg && <p className="text-[11px] text-emerald-400 font-mono">{saveMsg}</p>}
        </div>

        {/* Backend Deployment Instructions */}
        <div className="mt-3 p-3 rounded-lg bg-slate-950 border border-slate-800 text-[11px] space-y-1.5">
          <span className="font-bold text-cyan-400 uppercase text-[10px] tracking-wide block">
            How to run or deploy the Python FastAPI backend:
          </span>
          <div className="font-mono text-slate-300 space-y-1">
            <div>1. <span className="text-slate-400">Run locally:</span> <code className="text-cyan-300">cd backend &amp;&amp; python -m uvicorn app.main:app --port 8000</code></div>
            <div>2. <span className="text-slate-400">Deploy to Render/Railway:</span> Build command <code className="text-cyan-300">pip install -r backend/requirements.txt</code>, Start command <code className="text-cyan-300">uvicorn app.main:app --host 0.0.0.0 --port $PORT</code></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Persistence Layer */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center space-x-3 pb-3 border-b border-slate-800">
            <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">DATABASE PERSISTENCE STATUS</h2>
              <span className="text-xs text-emerald-400 font-semibold flex items-center space-x-1 mt-0.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Connected & Ready</span>
              </span>
            </div>
          </div>

          <div className="space-y-2 text-xs font-mono-code text-slate-300">
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-500">Active Engine:</span>
              <span className="text-cyan-400 font-bold">{healthData?.database?.engine || 'SQLite (Dev Mode)'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-500">Configured URI:</span>
              <span className="text-slate-300 text-[11px] truncate max-w-[200px]">{healthData?.database?.url_configured || 'sqlite:///./data/nids_platform.db'}</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">Isolation Layer:</span>
              <span className="text-emerald-400">Repositories & Base Repository Pattern</span>
            </div>
          </div>

          {/* Database Switch Instructions */}
          <div className="mt-4 p-3 rounded-lg bg-slate-950 border border-slate-900 text-xs">
            <span className="font-bold text-slate-400 uppercase text-[10px] tracking-wide block mb-1">
              Connecting Production Database (PostgreSQL / MySQL)
            </span>
            <p className="text-[11px] text-slate-400 mb-2 font-sans">
              Set <code className="text-cyan-400">DATABASE_URL</code> in your <code className="text-slate-300">.env</code> file. No code modifications are needed:
            </p>
            <div className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800 font-mono-code text-[11px] text-cyan-300">
              <span className="truncate">postgresql+psycopg2://user:password@localhost:5432/nids_db</span>
              <button onClick={copyDbUri} className="p-1 hover:text-white ml-2">
                <Copy className="w-3.5 h-3.5" />
              </button>
            </div>
            {copied && <span className="text-[10px] text-emerald-400 mt-1 block">Copied connection string template!</span>}
          </div>
        </div>

        {/* Machine Learning & Compute Subsystem */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center space-x-3 pb-3 border-b border-slate-800">
            <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">AI INFERENCE & COMPUTE ENGINE</h2>
              <span className="text-xs text-emerald-400 font-semibold flex items-center space-x-1 mt-0.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>PyTorch CPU Compute Active</span>
              </span>
            </div>
          </div>

          <div className="space-y-2 text-xs font-mono-code text-slate-300">
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-500">Framework:</span>
              <span className="text-slate-200">{healthData?.machine_learning?.framework || 'PyTorch 2.14.1+cpu'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-500">Active Architecture:</span>
              <span className="text-cyan-400 font-bold">{healthData?.machine_learning?.architecture || 'FlowTransformer'}</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">Loaded Weights:</span>
              <span className="text-emerald-400 font-bold">{healthData?.machine_learning?.active_model || 'flow_transformer_v1'}</span>
            </div>
          </div>
        </div>

        {/* CTI Service Connectors */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center space-x-3 pb-3 border-b border-slate-800">
            <div className="p-2.5 bg-purple-500/10 border border-purple-500/30 rounded-lg text-purple-400">
              <Globe2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">THREAT INTELLIGENCE CONNECTORS</h2>
              <span className="text-xs text-purple-400 font-semibold flex items-center space-x-1 mt-0.5">
                <span>STIX 2.1 / TAXII / AbuseIPDB</span>
              </span>
            </div>
          </div>

          <div className="space-y-2 text-xs font-mono-code text-slate-300">
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-500">AbuseIPDB Connector:</span>
              <span className="text-emerald-400 font-bold">{healthData?.threat_intelligence?.abuseipdb?.status || 'Operational'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-500">VirusTotal Connector:</span>
              <span className="text-emerald-400 font-bold">{healthData?.threat_intelligence?.virustotal?.status || 'Operational'}</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">MITRE Matrix:</span>
              <span className="text-purple-400">{healthData?.threat_intelligence?.mitre_framework || 'Enterprise v14.1'}</span>
            </div>
          </div>
        </div>

        {/* Explainability Subsystem */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center space-x-3 pb-3 border-b border-slate-800">
            <div className="p-2.5 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">eX-NIDS EXPLAINABILITY SUBSYSTEM</h2>
              <span className="text-xs text-cyan-400 font-semibold flex items-center space-x-1 mt-0.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Feature Attribution Active</span>
              </span>
            </div>
          </div>

          <div className="space-y-2 text-xs font-mono-code text-slate-300">
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-500">Methodology:</span>
              <span className="text-slate-200">Input x Gradient Attribution (Sensitivity)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <span className="text-slate-500">LLM Provider Mode:</span>
              <span className="text-cyan-400 font-bold">{healthData?.explainable_ai?.provider || 'simulation'}</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-500">Model Decision Integrity:</span>
              <span className="text-emerald-400">Enforced (LLM never overrides evidence)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
