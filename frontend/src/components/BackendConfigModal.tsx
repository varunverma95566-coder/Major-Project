import React, { useState, useEffect } from 'react';
import { Server, Wifi, WifiOff, CheckCircle2, AlertCircle, RefreshCw, ExternalLink } from 'lucide-react';
import { api } from '../services/api';
import { useToast } from '../context/ToastContext';

interface BackendConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStatusChange?: (isOnline: boolean) => void;
}

export const BackendConfigModal: React.FC<BackendConfigModalProps> = ({
  isOpen,
  onClose,
  onStatusChange
}) => {
  const { showToast } = useToast();
  const [apiUrl, setApiUrl] = useState<string>('');
  const [isTesting, setIsTesting] = useState<boolean>(false);
  const [status, setStatus] = useState<'unknown' | 'online' | 'offline'>('unknown');
  const [healthInfo, setHealthInfo] = useState<any>(null);

  useEffect(() => {
    if (isOpen) {
      const current = api.getApiBase();
      setApiUrl(current);
      checkStatus(current);
    }
  }, [isOpen]);

  const checkStatus = async (urlToCheck?: string) => {
    setIsTesting(true);
    try {
      const target = urlToCheck !== undefined ? urlToCheck : apiUrl;
      const res = await api.checkBackendHealth(target);
      if (res.online) {
        setStatus('online');
        setHealthInfo(res.details);
        if (onStatusChange) onStatusChange(true);
      } else {
        setStatus('offline');
        setHealthInfo(null);
        if (onStatusChange) onStatusChange(false);
      }
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = async () => {
    api.setApiBase(apiUrl);
    await checkStatus(apiUrl);
    showToast(
      'Backend Config Saved',
      apiUrl ? `Target API endpoint updated to: ${apiUrl}` : 'Reset to default static/dev endpoint.',
      'success'
    );
    onClose();
  };

  const handleReset = async () => {
    api.clearApiBase();
    setApiUrl(api.getApiBase());
    await checkStatus('');
    showToast('Reset to Default', 'Using default development/static endpoint.', 'info');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="glass-panel w-full max-w-lg rounded-2xl border border-slate-700 shadow-2xl p-6 relative">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-wide">
                BACKEND API CONNECTION
              </h2>
              <p className="text-[11px] text-slate-400">
                Connect your FastAPI Python inference engine to this frontend
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-lg font-mono p-1"
          >
            &times;
          </button>
        </div>

        {/* Current Status Pill */}
        <div className="my-4 p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {status === 'online' ? (
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                <Wifi className="w-4 h-4 animate-pulse" />
              </div>
            ) : (
              <div className="w-8 h-8 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
                <WifiOff className="w-4 h-4" />
              </div>
            )}
            <div>
              <div className="text-xs font-bold text-white flex items-center space-x-1.5">
                <span>{status === 'online' ? 'BACKEND CONNECTED' : 'STATIC DEMO / BACKEND OFFLINE'}</span>
                {status === 'online' && (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                )}
              </div>
              <div className="text-[10px] text-slate-400 font-mono">
                {status === 'online'
                  ? `Active Model: ${healthInfo?.active_model || 'flow_transformer_bigflow_v2'}`
                  : 'Displaying benchmark baseline telemetry'}
              </div>
            </div>
          </div>
          <button
            onClick={() => checkStatus()}
            disabled={isTesting}
            className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 flex items-center space-x-1 font-mono"
          >
            <RefreshCw className={`w-3 h-3 ${isTesting ? 'animate-spin' : ''}`} />
            <span>Ping</span>
          </button>
        </div>

        {/* Notice on GitHub Pages vs Backend */}
        <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-800/40 text-[11px] text-cyan-200/90 space-y-1">
          <div className="font-bold flex items-center space-x-1 text-cyan-300">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>GitHub Pages Hosting Note:</span>
          </div>
          <p>
            GitHub Pages serves this web frontend statically. Real-time deep packet inference, live sensor capture, and BigFlow-NIDS parquet replay require a running FastAPI instance (<code className="text-cyan-400">python -m uvicorn app.main:app</code>).
          </p>
        </div>

        {/* Input Form */}
        <div className="mt-4 space-y-3">
          <div>
            <label className="block text-xs font-bold text-slate-300 mb-1 font-mono uppercase tracking-wider">
              Backend Endpoint URL:
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="e.g. https://your-fastapi-backend.onrender.com or http://localhost:8000"
                className="flex-1 px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-xs text-slate-100 font-mono focus:border-cyan-500 focus:outline-none"
              />
              <button
                type="button"
                onClick={() => checkStatus(apiUrl)}
                disabled={isTesting}
                className="px-3 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 text-xs font-bold"
              >
                Test
              </button>
            </div>
            <p className="text-[10px] text-slate-500 mt-1">
              Leave blank to use default Vite proxy (in local dev) or static mode.
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-6 flex items-center justify-between pt-4 border-t border-slate-800">
          <button
            onClick={handleReset}
            className="text-xs text-slate-400 hover:text-slate-200 underline font-mono"
          >
            Reset Default
          </button>
          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-semibold"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 text-xs font-bold shadow-md shadow-cyan-500/20"
            >
              Save Endpoint
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
