import React, { useState, useEffect } from 'react';
import { Globe2, Plus, RefreshCw, Search, ShieldAlert, CheckCircle, Shield, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import { IOC } from '../types/api';
import { SeverityBadge, StatusBadge } from '../components/Badge';
import { Modal } from '../components/Modal';
import { useToast } from '../context/ToastContext';

export const IOCExplorerPage: React.FC = () => {
  const [iocs, setIocs] = useState<IOC[]>([]);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState('');
  const [verificationFilter, setVerificationFilter] = useState('');
  const [search, setSearch] = useState('');
  const [enrichingId, setEnrichingId] = useState<number | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const { showToast } = useToast();

  // New IOC state
  const [newValue, setNewValue] = useState('');
  const [newType, setNewType] = useState('ipv4');
  const [newSeverity, setNewSeverity] = useState('Medium');
  const [newDesc, setNewDesc] = useState('');

  useEffect(() => {
    loadIOCs();
  }, [typeFilter, verificationFilter]);

  const loadIOCs = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (typeFilter) params.ioc_type = typeFilter;
      if (verificationFilter) params.verification_status = verificationFilter;
      if (search) params.search = search;
      const res = await api.getIOCs(params);
      setIocs(res.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEnrich = async (ioc: IOC) => {
    setEnrichingId(ioc.id);
    try {
      await api.enrichIndicator(ioc.value);
      await loadIOCs();
      showToast('Enrichment Completed', `Threat intelligence feeds enriched indicator ${ioc.value}`, 'success');
    } catch (err: any) {
      showToast('Enrichment Failed', err?.message || 'Failed to query threat intelligence feeds', 'danger');
    } finally {
      setEnrichingId(null);
    }
  };

  const handleCreateIOC = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createIOC({
        value: newValue,
        ioc_type: newType,
        severity: newSeverity,
        description: newDesc
      });
      setCreateModalOpen(false);
      const createdVal = newValue;
      setNewValue('');
      setNewDesc('');
      await loadIOCs();
      showToast('Custom IOC Created', `Registered indicator ${createdVal} (${newType}) into STIX 2.1 database`, 'success');
    } catch (err: any) {
      showToast('Creation Error', err?.message || 'Failed to save IOC', 'danger');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-wide" style={{ fontFamily: 'var(--font-display)' }}>
            INDICATORS OF COMPROMISE & CTI ENRICHMENT
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Strict separation of observed telemetry vs enrichment feeds vs analyst verification status
          </p>
        </div>

        <button
          onClick={() => setCreateModalOpen(true)}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center space-x-2 shadow-lg shadow-cyan-500/20"
        >
          <Plus className="w-4 h-4" />
          <span>Add Custom IOC</span>
        </button>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && loadIOCs()}
            placeholder="Search indicator by IP, domain, hash, or port..."
            className="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono-code"
          />
        </div>

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
        >
          <option value="">All IOC Types</option>
          <option value="ipv4">IPv4</option>
          <option value="domain">Domain</option>
          <option value="sha256">SHA-256 Hash</option>
          <option value="port">Port</option>
        </select>

        <select
          value={verificationFilter}
          onChange={(e) => setVerificationFilter(e.target.value)}
          className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
        >
          <option value="">All Verification Statuses</option>
          <option value="confirmed_malicious">Confirmed Malicious</option>
          <option value="suspicious">Suspicious</option>
          <option value="unverified">Unverified</option>
          <option value="benign_whitelisted">Benign / Whitelisted</option>
        </select>
      </div>

      {/* IOC Table */}
      <div className="glass-panel p-5 rounded-xl border border-slate-800 overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-500 font-semibold uppercase text-[10px] tracking-wider">
              <th className="pb-3">Indicator Value</th>
              <th className="pb-3">Type</th>
              <th className="pb-3">Observed Status</th>
              <th className="pb-3">Enrichment Status</th>
              <th className="pb-3">Verification Status</th>
              <th className="pb-3">Reputation</th>
              <th className="pb-3">Severity</th>
              <th className="pb-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-medium">
            {iocs.map((ioc) => (
              <tr key={ioc.id} className="hover:bg-slate-900/60 transition-colors">
                <td className="py-3 font-mono-code font-bold text-cyan-400">{ioc.value}</td>
                <td className="py-3 uppercase text-[11px] text-slate-400 font-semibold">{ioc.ioc_type}</td>
                <td className="py-3">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-300 border border-slate-700">
                    {ioc.observed_status}
                  </span>
                </td>
                <td className="py-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                    ioc.enrichment_status === 'enriched'
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                      : 'bg-slate-800 text-slate-400'
                  }`}>
                    {ioc.enrichment_status}
                  </span>
                </td>
                <td className="py-3">
                  <span className={`cyber-badge ${
                    ioc.verification_status === 'confirmed_malicious'
                      ? 'bg-rose-950 text-rose-300 border-rose-500/50'
                      : ioc.verification_status === 'suspicious'
                      ? 'bg-amber-950 text-amber-300 border-amber-500/50'
                      : 'bg-slate-800 text-slate-300 border-slate-700'
                  } border`}>
                    {ioc.verification_status.replace('_', ' ')}
                  </span>
                </td>
                <td className="py-3 font-mono-code text-slate-300">
                  {ioc.reputation_score !== null && ioc.reputation_score !== undefined
                    ? `${ioc.reputation_score}/100`
                    : 'Unscored'}
                </td>
                <td className="py-3">
                  <SeverityBadge severity={ioc.severity} />
                </td>
                <td className="py-3 text-right">
                  <button
                    onClick={() => handleEnrich(ioc)}
                    disabled={enrichingId === ioc.id}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded text-[11px] font-semibold flex items-center space-x-1 ml-auto disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3 h-3 ${enrichingId === ioc.id ? 'animate-spin' : ''}`} />
                    <span>{enrichingId === ioc.id ? 'Querying...' : 'Enrich Feed'}</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {iocs.length === 0 && !loading && (
          <div className="text-center py-12 text-slate-500 text-xs font-mono-code">
            No threat indicators found.
          </div>
        )}
      </div>

      {/* Add IOC Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Register New Threat Indicator (IOC)"
        subtitle="Manually register an external threat actor address or compromised asset"
      >
        <form onSubmit={handleCreateIOC} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Indicator Value *</label>
            <input
              type="text"
              required
              value={newValue}
              onChange={(e) => setNewValue(e.target.value)}
              placeholder="e.g. 91.240.118.12 or bad-domain.net"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono-code"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">IOC Type</label>
              <select
                value={newType}
                onChange={(e) => setNewType(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200"
              >
                <option value="ipv4">IPv4 Address</option>
                <option value="domain">Domain Name</option>
                <option value="sha256">SHA-256 Hash</option>
                <option value="port">Suspicious Port</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Initial Severity</label>
              <select
                value={newSeverity}
                onChange={(e) => setNewSeverity(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200"
              >
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Threat Context & Notes</label>
            <textarea
              rows={2}
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="Observed in outbound command-and-control connection..."
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => setCreateModalOpen(false)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs rounded-lg uppercase tracking-wider"
            >
              Save & Auto-Enrich
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
