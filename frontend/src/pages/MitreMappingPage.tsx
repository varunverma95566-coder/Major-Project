import React, { useState, useEffect } from 'react';
import { ShieldAlert, ExternalLink, ShieldCheck, Search, Filter } from 'lucide-react';
import { api } from '../services/api';
import { MitreTechnique } from '../types/api';

export const MitreMappingPage: React.FC = () => {
  const [techniques, setTechniques] = useState<MitreTechnique[]>([]);
  const [loading, setLoading] = useState(true);
  const [tacticFilter, setTacticFilter] = useState('');

  useEffect(() => {
    loadTechniques();
  }, []);

  const loadTechniques = async () => {
    try {
      setLoading(true);
      const data = await api.getMitreTechniques();
      setTechniques(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const tactics = Array.from(new Set(techniques.map(t => t.tactic)));
  const filtered = tacticFilter ? techniques.filter(t => t.tactic === tacticFilter) : techniques;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-wide" style={{ fontFamily: 'var(--font-display)' }}>
            MITRE ATT&CK ENTERPRISE MATRIX (v14.1) MAPPING
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Empirical grounding of FlowTransformer attack categories to standardized adversarial techniques
          </p>
        </div>

        <select
          value={tacticFilter}
          onChange={(e) => setTacticFilter(e.target.value)}
          className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
        >
          <option value="">All MITRE Tactics</option>
          {tactics.map(t => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      {/* Grid of Techniques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((tech) => (
          <div
            key={tech.id}
            className="glass-panel p-6 rounded-xl border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all shadow-md group"
          >
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-mono-code font-bold text-xs text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
                    {tech.technique_id}
                  </span>
                  <h2 className="text-base font-bold text-white tracking-wide mt-2">{tech.name}</h2>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-purple-500/10 text-purple-300 border border-purple-500/30">
                  {tech.tactic}
                </span>
              </div>

              <p className="text-xs text-slate-300 mt-3 line-clamp-3 font-sans">
                {tech.description}
              </p>

              {/* Mapping Rationale */}
              <div className="mt-4 p-3 rounded-lg bg-slate-950/80 border border-slate-800/80 text-xs">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                  Detection Rationale
                </span>
                <p className="text-slate-300 font-sans italic text-[11px]">
                  "{tech.mapping_rationale}"
                </p>
              </div>

              {/* Target attack categories */}
              <div className="mt-3 flex flex-wrap gap-1">
                {tech.attack_categories?.map((c, i) => (
                  <span key={i} className="px-2 py-0.5 rounded text-[10px] bg-slate-900 border border-slate-800 font-mono-code text-cyan-400">
                    {c}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-slate-500 text-[11px]">
                Confidence Weight: <strong className="text-emerald-400 font-mono-code">{(tech.confidence_weight * 100).toFixed(0)}%</strong>
              </span>
              {tech.url && (
                <a
                  href={tech.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 hover:text-cyan-300 font-semibold flex items-center space-x-1"
                >
                  <span>MITRE Matrix</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
