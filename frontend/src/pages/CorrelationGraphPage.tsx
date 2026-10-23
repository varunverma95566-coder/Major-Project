import React, { useState, useEffect } from 'react';
import { Share2, RefreshCw, Shield, AlertTriangle, Filter, Globe2, AlertOctagon } from 'lucide-react';
import { api } from '../services/api';
import { GraphNode, GraphEdge } from '../types/api';
import { SeverityBadge } from '../components/Badge';

export const CorrelationGraphPage: React.FC = () => {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    loadGraph();
  }, []);

  const loadGraph = async () => {
    try {
      setLoading(true);
      const data = await api.getCorrelationGraph();
      setNodes(data.nodes);
      setEdges(data.edges);
      if (data.nodes.length > 0) setSelectedNode(data.nodes[0]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-wide" style={{ fontFamily: 'var(--font-display)' }}>
            THREAT RELATIONSHIP & CORRELATION GRAPH
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Graph topology correlating attacker IP infrastructure, flow alerts, MITRE techniques, and incidents
          </p>
        </div>

        <button
          onClick={loadGraph}
          className="px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-semibold text-slate-300 flex items-center space-x-2 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-correlate Graph</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interactive Visual Canvas Container */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800 lg:col-span-2 min-h-[500px] flex flex-col justify-between relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-4 z-10">
            <span className="font-mono-code">Entities: {nodes.length} | Relationships: {edges.length}</span>
            <div className="flex items-center space-x-3">
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                <span className="text-[11px]">IOC (IP)</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                <span className="text-[11px]">Alert</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                <span className="text-[11px]">Incident</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-purple-400"></span>
                <span className="text-[11px]">MITRE</span>
              </span>
            </div>
          </div>

          {/* Node Canvas / Relationship Matrix */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 my-auto py-4 z-10">
            {nodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              let borderColor = 'border-slate-800';
              let badgeBg = 'bg-slate-800 text-slate-300';
              if (node.type === 'ioc') {
                borderColor = isSelected ? 'border-cyan-400 shadow-cyan-500/20' : 'border-cyan-500/30';
                badgeBg = 'bg-cyan-500/10 text-cyan-400';
              } else if (node.type === 'alert') {
                borderColor = isSelected ? 'border-amber-400 shadow-amber-500/20' : 'border-amber-500/30';
                badgeBg = 'bg-amber-500/10 text-amber-400';
              } else if (node.type === 'incident') {
                borderColor = isSelected ? 'border-rose-400 shadow-rose-500/20' : 'border-rose-500/30';
                badgeBg = 'bg-rose-500/10 text-rose-400';
              } else if (node.type === 'mitre') {
                borderColor = isSelected ? 'border-purple-400 shadow-purple-500/20' : 'border-purple-500/30';
                badgeBg = 'bg-purple-500/10 text-purple-400';
              }

              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`p-3.5 rounded-xl border bg-slate-950/80 cursor-pointer transition-all shadow-md ${borderColor} ${
                    isSelected ? 'scale-105 shadow-lg' : 'hover:scale-[1.02]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase ${badgeBg}`}>
                      {node.type}
                    </span>
                    {node.severity && <SeverityBadge severity={node.severity} />}
                  </div>
                  <div className="font-mono-code text-xs font-bold text-white truncate">{node.label}</div>
                  <div className="text-[10px] text-slate-500 font-mono-code mt-1 truncate">ID: {node.id}</div>
                </div>
              );
            })}
          </div>

          {/* Relationships ticker */}
          <div className="pt-3 border-t border-slate-900 z-10 flex flex-wrap gap-2">
            {edges.slice(0, 5).map((e) => (
              <span key={e.id} className="text-[10px] font-mono-code px-2 py-1 rounded bg-slate-900 border border-slate-800 text-slate-400">
                {e.source.split(':')[1]} &rarr; [{e.relationship}] &rarr; {e.target.split(':')[1]}
              </span>
            ))}
          </div>
        </div>

        {/* Selected Entity Details Panel */}
        <div className="glass-panel p-6 rounded-xl border border-slate-800">
          <h2 className="text-sm font-bold text-white tracking-wide mb-4" style={{ fontFamily: 'var(--font-display)' }}>
            ENTITY EVIDENCE & CORRELATION
          </h2>

          {selectedNode ? (
            <div className="space-y-4">
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase font-bold font-mono-code">Entity Node ID</span>
                <div className="text-sm font-bold font-mono-code text-cyan-400 mt-0.5 break-all">
                  {selectedNode.id}
                </div>
                <div className="mt-2 text-xs text-slate-200 font-bold">{selectedNode.label}</div>
              </div>

              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Connected Links</h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {edges
                    .filter((e) => e.source === selectedNode.id || e.target === selectedNode.id)
                    .map((edge) => (
                      <div key={edge.id} className="p-2.5 rounded bg-slate-950 border border-slate-800/80 text-xs">
                        <div className="text-cyan-400 font-semibold">{edge.relationship}</div>
                        <div className="text-[11px] text-slate-400 font-mono-code mt-0.5">
                          {edge.source === selectedNode.id ? `Target: ${edge.target}` : `Source: ${edge.source}`}
                        </div>
                        <div className="text-[10px] text-slate-500 mt-1">Confidence: {edge.confidence * 100}%</div>
                      </div>
                    ))}
                </div>
              </div>

              {/* Node Details Snapshot */}
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Node Attributes</h3>
                <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800/80 font-mono-code text-xs text-slate-300 space-y-1">
                  {Object.entries(selectedNode.details || {}).map(([k, v]) => (
                    <div key={k} className="flex justify-between">
                      <span className="text-slate-500">{k}:</span>
                      <span className="text-slate-200">{String(v)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-slate-500 text-xs py-12 text-center">Select an entity in the graph to inspect evidence.</div>
          )}
        </div>
      </div>
    </div>
  );
};
