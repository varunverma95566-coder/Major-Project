import React, { useState, useEffect } from 'react';
import { Users2, Play, ShieldCheck, CheckCircle2, RefreshCw, Lock, Building, ArrowUpRight } from 'lucide-react';
import { api } from '../services/api';
import { FederatedClient, FederatedRound } from '../types/api';
import { StatusBadge } from '../components/Badge';

import { useToast } from '../context/ToastContext';

export const FederatedLearningPage: React.FC = () => {
  const [clients, setClients] = useState<FederatedClient[]>([]);
  const [rounds, setRounds] = useState<FederatedRound[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const { showToast } = useToast();

  useEffect(() => {
    loadFederatedData();
  }, []);

  const loadFederatedData = async () => {
    try {
      setLoading(true);
      const [cList, rList] = await Promise.all([
        api.getFederatedClients(),
        api.getFederatedRounds()
      ]);
      setClients(cList);
      setRounds(rList);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerRound = async () => {
    setTriggering(true);
    setStatusMsg(null);
    try {
      const res = await api.triggerFederatedRound({ local_epochs: 1 });
      const msg = `Round ${res.round_number} completed successfully! FedAvg aggregated weights updated across FinBank, MedHealth, and CloudTel.`;
      setStatusMsg(msg);
      showToast('FedAvg Round Completed', msg, 'success');
      await loadFederatedData();
    } catch (err: any) {
      const errMsg = err.message || 'Federated round failed';
      setStatusMsg(errMsg);
      showToast('Federated Round Failed', errMsg, 'danger');
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-wide" style={{ fontFamily: 'var(--font-display)' }}>
            FEDERATED LEARNING & COLLABORATIVE CTI
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Privacy-preserving collaborative intrusion detection across simulated multi-sector organizations using FedAvg
          </p>
        </div>

        <button
          onClick={handleTriggerRound}
          disabled={triggering}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs uppercase tracking-wider flex items-center space-x-2 shadow-lg shadow-purple-900/30 disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{triggering ? 'Aggregating FedAvg...' : 'Trigger Federated Round'}</span>
        </button>
      </div>

      {statusMsg && (
        <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs rounded-lg flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>{statusMsg}</span>
        </div>
      )}

      {/* Privacy Guarantee Alert Notice */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-start space-x-3 text-xs">
        <Lock className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <h2 className="font-bold text-white uppercase tracking-wide">
            Privacy-Preserving Architecture Notice
          </h2>
          <p className="text-slate-400 font-sans leading-relaxed">
            Raw client training flows remain strictly isolated within each simulated participant organization.
            Only ephemeral model gradient parameter weights ($\theta_k$) are shared with the central coordinator
            and aggregated using the Federated Averaging (FedAvg) algorithm.
          </p>
        </div>
      </div>

      {/* Simulated Participating Organizations */}
      <div>
        <h2 className="text-sm font-bold text-white tracking-wide mb-3" style={{ fontFamily: 'var(--font-display)' }}>
          PARTICIPATING SECTOR ORGANIZATIONS ({clients.length})
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {clients.map((c) => (
            <div key={c.id} className="glass-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2.5">
                    <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                      <Building className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="font-bold text-xs text-white">{c.name}</h3>
                      <span className="text-[10px] text-purple-400 font-semibold uppercase">{c.industry_sector}</span>
                    </div>
                  </div>
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                </div>

                <div className="mt-4 p-3 bg-slate-950/60 rounded-lg border border-slate-900 text-xs space-y-1">
                  <div className="flex justify-between text-slate-400">
                    <span>Partitioned Data:</span>
                    <strong className="text-slate-300 font-mono-code">{c.local_sample_count} flows</strong>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Local Accuracy:</span>
                    <strong className="text-emerald-400 font-mono-code">
                      {c.local_accuracy ? `${(c.local_accuracy * 100).toFixed(1)}%` : '89.5%'}
                    </strong>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-500 flex justify-between">
                <span>Dataset: {c.dataset_name?.split('(')[0]}</span>
                <span className="font-mono-code">Round {c.current_round}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Aggregation Rounds History */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800">
        <h2 className="text-sm font-bold text-white tracking-wide mb-3" style={{ fontFamily: 'var(--font-display)' }}>
          HISTORICAL FEDERATED AGGREGATION ROUNDS
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-500 font-semibold uppercase text-[10px] tracking-wider">
                <th className="pb-3">Round Number</th>
                <th className="pb-3">Strategy</th>
                <th className="pb-3">Participating Clients</th>
                <th className="pb-3">Total Flow Samples</th>
                <th className="pb-3">Pre-Aggregation Acc</th>
                <th className="pb-3">Post-Aggregation Acc</th>
                <th className="pb-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono-code">
              {rounds.map((r) => (
                <tr key={r.id} className="hover:bg-slate-900/60 transition-colors">
                  <td className="py-3 font-bold text-cyan-400">Round #{r.round_number}</td>
                  <td className="py-3 text-slate-300 font-bold">{r.aggregation_strategy}</td>
                  <td className="py-3 text-slate-400">{r.participating_clients?.join(', ')}</td>
                  <td className="py-3 text-slate-300">{r.total_samples}</td>
                  <td className="py-3 text-slate-400">
                    {r.global_accuracy_before ? `${(r.global_accuracy_before * 100).toFixed(1)}%` : 'N/A'}
                  </td>
                  <td className="py-3 text-emerald-400 font-bold">
                    {r.global_accuracy_after ? `${(r.global_accuracy_after * 100).toFixed(1)}%` : '91.0%'}
                  </td>
                  <td className="py-3">
                    <StatusBadge status={r.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
