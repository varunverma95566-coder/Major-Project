import React, { useState, useEffect } from 'react';
import { FileText, Download, Share2, FileCode, CheckCircle2, ShieldAlert } from 'lucide-react';
import { api } from '../services/api';

export const ReportsPage: React.FC = () => {
  const [reportMarkdown, setReportMarkdown] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadReport();
  }, []);

  const loadReport = async () => {
    try {
      setLoading(true);
      const res = await api.getExecutiveReport();
      setReportMarkdown(res.report_markdown);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const downloadMarkdown = () => {
    window.open('/api/reports/download', '_blank');
  };

  const downloadStix = async () => {
    try {
      const res = await fetch('/api/cti/export/stix');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'cyber_sentinel_stix21_bundle.json';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
    }
  };

  const downloadCsv = () => {
    window.open('/api/cti/export/csv', '_blank');
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-wide" style={{ fontFamily: 'var(--font-display)' }}>
            REPORTS & STANDARDIZED CTI EXPORT (STIX 2.1)
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Export threat intelligence, evaluation audits, and incident narratives for TAXII server integration
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={downloadCsv}
            className="px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-semibold text-slate-200 flex items-center space-x-1.5 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Export IOC CSV</span>
          </button>

          <button
            onClick={downloadStix}
            className="px-3.5 py-1.5 rounded-lg bg-purple-950/40 hover:bg-purple-950/70 border border-purple-800 text-xs font-semibold text-purple-300 flex items-center space-x-1.5 transition-colors"
          >
            <Share2 className="w-3.5 h-3.5 text-purple-400" />
            <span>Export STIX 2.1 Bundle</span>
          </button>

          <button
            onClick={downloadMarkdown}
            className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center space-x-1.5 shadow-lg shadow-cyan-500/20"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Download Report (.md)</span>
          </button>
        </div>
      </div>

      {/* Report Preview Document */}
      <div className="glass-panel p-8 rounded-xl border border-slate-800">
        <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-800">
          <span className="text-xs font-bold font-mono-code text-cyan-400 uppercase tracking-wider">
            EXECUTIVE INTELLIGENCE BRIEFING // LIVE GENERATED
          </span>
          <span className="text-xs text-slate-500">Autonomous SOC Synthesis</span>
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-500 text-xs font-mono-code">
            Compiling report from active model weights and security alerts...
          </div>
        ) : (
          <div className="bg-slate-950 p-6 rounded-xl border border-slate-900 font-mono-code text-xs text-slate-300 leading-relaxed whitespace-pre-wrap max-h-[600px] overflow-y-auto">
            {reportMarkdown}
          </div>
        )}
      </div>
    </div>
  );
};
