import React from 'react';

interface SeverityBadgeProps {
  severity: string;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity }) => {
  const s = severity?.toLowerCase() || 'medium';
  
  if (s === 'critical') {
    return (
      <span className="cyber-badge bg-rose-950/80 text-rose-300 border border-rose-500/50 shadow-sm shadow-rose-900/40">
        <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mr-1.5 animate-ping"></span>
        Critical
      </span>
    );
  }
  if (s === 'high') {
    return (
      <span className="cyber-badge bg-amber-950/80 text-amber-300 border border-amber-500/50">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mr-1.5"></span>
        High
      </span>
    );
  }
  if (s === 'medium') {
    return (
      <span className="cyber-badge bg-yellow-950/60 text-yellow-300 border border-yellow-500/40">
        <span className="w-1.5 h-1.5 rounded-full bg-yellow-400 mr-1.5"></span>
        Medium
      </span>
    );
  }
  if (s === 'low') {
    return (
      <span className="cyber-badge bg-blue-950/60 text-blue-300 border border-blue-500/40">
        <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mr-1.5"></span>
        Low
      </span>
    );
  }
  return (
    <span className="cyber-badge bg-slate-800 text-slate-300 border border-slate-700">
      <span className="w-1.5 h-1.5 rounded-full bg-slate-400 mr-1.5"></span>
      Info
    </span>
  );
};

export const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const st = status?.toLowerCase() || 'new';
  let color = 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
  
  if (st === 'investigating' || st === 'in progress') {
    color = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
  } else if (st === 'resolved' || st === 'closed' || st === 'trained' || st === 'confirmed_malicious') {
    color = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  } else if (st === 'false positive') {
    color = 'bg-slate-700/50 text-slate-400 border-slate-600';
  }

  return (
    <span className={`cyber-badge ${color} border`}>
      {status}
    </span>
  );
};
