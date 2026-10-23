import React, { useState, useEffect } from 'react';
import { Search, Filter, ShieldAlert, Cpu, Bot, ArrowRight, Eye, ChevronRight } from 'lucide-react';
import { api } from '../services/api';
import { Prediction } from '../types/api';
import { SeverityBadge } from '../components/Badge';
import { Modal } from '../components/Modal';

export const FlowInvestigationPage: React.FC = () => {
  const [flows, setFlows] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filterClass, setFilterClass] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('');
  const [filterSource, setFilterSource] = useState('');
  const [availableClasses, setAvailableClasses] = useState<string[]>([]);
  const [selectedFlow, setSelectedFlow] = useState<Prediction | null>(null);

  // Load active model classes dynamically
  useEffect(() => {
    const loadModelClasses = async () => {
      try {
        const models = await api.getModels();
        const active = models.find((m) => m.is_active) || models[0];
        if (active && active.target_classes) {
          setAvailableClasses(active.target_classes);
        } else {
          const cats = await api.getBigFlowCategories();
          setAvailableClasses(cats.categories.map((c) => c.name));
        }
      } catch (err) {
        console.error('Failed to load active model classes:', err);
      }
    };
    loadModelClasses();
  }, []);

  useEffect(() => {
    loadFlows();
  }, [page, filterClass, filterSeverity, filterSource]);

  const loadFlows = async () => {
    try {
      setLoading(true);
      const params: any = { page, page_size: 20 };
      if (filterClass) params.predicted_class = filterClass;
      if (filterSeverity) params.severity = filterSeverity;
      if (filterSource) params.ingestion_source = filterSource;
      const res = await api.getPredictions(params);
      setFlows(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getSourceBadge = (source?: string, isSimulated?: boolean) => {
    if (isSimulated || source === 'simulated_preset') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          Simulated
        </span>
      );
    }
    if (source === 'file_upload') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-500/10 text-purple-400 border border-purple-500/30">
          File Upload
        </span>
      );
    }
    if (source === 'dataset_replay') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
          BigFlow Replay
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
        Live Monitored
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-wide" style={{ fontFamily: 'var(--font-display)' }}>
            FLOW TELEMETRY &amp; eX-NIDS EXPLAINABILITY
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Feature-level gradient attribution and grounded AI explanation for analyzed packet streams
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={filterSource}
            onChange={(e) => setFilterSource(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
          >
            <option value="">All Ingestion Sources</option>
            <option value="live_capture">Live Monitoring</option>
            <option value="dataset_replay">BigFlow Replay</option>
            <option value="file_upload">Uploaded Flow File</option>
            <option value="simulated_preset">Simulated Presets</option>
          </select>

          <select
            value={filterClass}
            onChange={(e) => setFilterClass(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
          >
            <option value="">All Attack Classes ({availableClasses.length})</option>
            <option value="Unknown / Suspicious Anomaly">Unknown / Suspicious Anomaly</option>
            {availableClasses.map((clsName) => (
              <option key={clsName} value={clsName}>
                {clsName}
              </option>
            ))}
          </select>

          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
          >
            <option value="">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
            <option value="Informational">Informational</option>
          </select>
        </div>
      </div>

      {/* Main Flow Table */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-500 font-semibold uppercase text-[10px] tracking-wider">
              <th className="pb-3">Flow ID</th>
              <th className="pb-3">Source &amp; Destination</th>
              <th className="pb-3">Protocol / Port</th>
              <th className="pb-3">Ingestion Source</th>
              <th className="pb-3">Model Prediction</th>
              <th className="pb-3">Confidence</th>
              <th className="pb-3">Risk Score</th>
              <th className="pb-3">Severity</th>
              <th className="pb-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-medium">
            {flows.map((flow) => (
              <tr
                key={flow.id}
                onClick={() => setSelectedFlow(flow)}
                className="hover:bg-slate-900/60 cursor-pointer transition-colors"
              >
                <td className="py-3 font-mono text-cyan-400 font-bold">{flow.flow_id}</td>
                <td className="py-3 font-mono text-slate-300">
                  {flow.src_ip} &rarr; {flow.dst_ip}
                </td>
                <td className="py-3 font-mono text-slate-400">
                  {flow.protocol} / {flow.dst_port}
                </td>
                <td className="py-3">
                  {getSourceBadge(flow.ingestion_source, flow.is_simulated)}
                </td>
                <td className="py-3">
                  <div className="flex flex-col">
                    <span
                      className={`font-semibold flex items-center space-x-1.5 ${
                        flow.is_anomaly
                          ? 'text-amber-400 font-bold'
                          : flow.is_malicious
                          ? 'text-rose-400'
                          : 'text-emerald-400'
                      }`}
                    >
                      {flow.is_anomaly && (
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                      )}
                      <span>{flow.predicted_class}</span>
                    </span>
                    {flow.ground_truth_attack && flow.ground_truth_attack !== flow.predicted_class && (
                      <span className="text-[10px] text-slate-500 font-mono">
                        GT: {flow.ground_truth_attack}
                      </span>
                    )}
                  </div>
                </td>
                <td className="py-3 font-mono text-slate-300">
                  {(flow.confidence * 100).toFixed(1)}%
                </td>
                <td className="py-3 font-mono font-bold text-white">{flow.risk_score}</td>
                <td className="py-3">
                  <SeverityBadge severity={flow.severity} />
                </td>
                <td className="py-3 text-right">
                  <button className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded text-[11px] font-semibold flex items-center space-x-1 ml-auto">
                    <span>Inspect</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {flows.length === 0 && !loading && (
          <div className="text-center py-12 text-slate-500 text-xs font-mono">
            No flows match filter criteria.
          </div>
        )}
      </div>

      {/* Investigation Details Modal */}
      {selectedFlow && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedFlow(null)}
          title={`FLOW TELEMETRY INSPECTION // ${selectedFlow.flow_id}`}
          subtitle={`Analyzed by FlowTransformer (${selectedFlow.model_version || 'v1.0.0'})`}
          maxWidth="max-w-3xl"
        >
          <div className="space-y-6">
            {/* Top Summary Banner */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 bg-slate-950 rounded-xl border border-slate-800 text-center">
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-semibold">Classification</span>
                <div className="text-sm font-bold text-rose-400 mt-0.5">{selectedFlow.predicted_class}</div>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-semibold">Model Confidence</span>
                <div className="text-sm font-bold font-mono-code text-cyan-400 mt-0.5">
                  {(selectedFlow.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-semibold">Calculated Risk</span>
                <div className="text-sm font-bold font-mono-code text-white mt-0.5">{selectedFlow.risk_score} / 100</div>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-semibold">Severity Rating</span>
                <div className="mt-1">
                  <SeverityBadge severity={selectedFlow.severity} />
                </div>
              </div>
            </div>

            {/* Human Grounded Explanation */}
            <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800">
              <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                <Cpu className="w-4 h-4" />
                <span>Grounded FlowTransformer Detection Explanation</span>
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                {selectedFlow.human_explanation || 'Telemetry analyzed within operational thresholds.'}
              </p>
            </div>

            {/* eX-NIDS Feature Attribution Bar Chart */}
            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                Feature-Level Attribution Scores (Input x Gradient Sensitivity)
              </h3>
              <div className="space-y-2.5">
                {selectedFlow.feature_importances?.map((item, idx) => {
                  const isRisk = item.direction === 'increases_risk';
                  return (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-mono-code text-slate-300">
                          {item.feature}: <strong className="text-cyan-400">{String(item.value)}</strong>
                        </span>
                        <span
                          className={`font-mono-code font-bold ${
                            isRisk ? 'text-rose-400' : 'text-emerald-400'
                          }`}
                        >
                          {item.contribution > 0 ? `+${item.contribution}` : item.contribution} ({item.direction.replace('_', ' ')})
                        </span>
                      </div>
                      <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-1.5 rounded-full ${
                            isRisk ? 'bg-rose-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${Math.min(Math.abs(item.contribution) * 100, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* LLM Interpretation Section */}
            {selectedFlow.llm_interpretation && (
              <div className="p-4 bg-purple-950/20 border border-purple-900/40 rounded-xl">
                <h3 className="text-xs font-bold text-purple-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <Bot className="w-4 h-4" />
                  <span>Synthesized CTI Narrative (eX-NIDS Interface)</span>
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed italic">
                  "{selectedFlow.llm_interpretation}"
                </p>
                <div className="mt-2 text-[10px] text-slate-500">
                  Note: Distinguishes natural-language narrative synthesis from verified model mathematical evidence.
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
};
