import React, { useState, useEffect } from 'react';
import { AlertOctagon, Plus, CheckCircle2, Clock, ShieldAlert, ArrowRight, User } from 'lucide-react';
import { api } from '../services/api';
import { Incident } from '../types/api';
import { SeverityBadge, StatusBadge } from '../components/Badge';
import { Modal } from '../components/Modal';

export const IncidentsPage: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);

  // Create Form State
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newSeverity, setNewSeverity] = useState('High');
  const [newAssets, setNewAssets] = useState('');
  const [newIOCs, setNewIOCs] = useState('');

  // Update Form State
  const [updateStatus, setUpdateStatus] = useState('');
  const [newTimelineEvent, setNewTimelineEvent] = useState('');
  const [rootCause, setRootCause] = useState('');
  const [mitigation, setMitigation] = useState('');

  useEffect(() => {
    loadIncidents();
  }, []);

  const loadIncidents = async () => {
    try {
      setLoading(true);
      const data = await api.getIncidents();
      setIncidents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        title: newTitle,
        description: newDesc,
        severity: newSeverity,
        affected_assets: newAssets.split(',').map(s => s.trim()).filter(Boolean),
        associated_iocs: newIOCs.split(',').map(s => s.trim()).filter(Boolean)
      };
      await api.createIncident(payload);
      setCreateModalOpen(false);
      setNewTitle('');
      setNewDesc('');
      setNewAssets('');
      setNewIOCs('');
      await loadIncidents();
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIncident) return;
    try {
      const payload: any = {};
      if (updateStatus) payload.status = updateStatus;
      if (newTimelineEvent) payload.new_timeline_event = newTimelineEvent;
      if (rootCause) payload.root_cause = rootCause;
      if (mitigation) payload.mitigation_steps = mitigation;

      const updated = await api.updateIncident(selectedIncident.id, payload);
      setSelectedIncident(updated);
      setNewTimelineEvent('');
      await loadIncidents();
    } catch (err) {
      console.error(err);
    }
  };

  const openIncidentModal = (inc: Incident) => {
    setSelectedIncident(inc);
    setUpdateStatus(inc.status);
    setRootCause(inc.root_cause || '');
    setMitigation(inc.mitigation_steps || '');
    setNewTimelineEvent('');
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-wide" style={{ fontFamily: 'var(--font-display)' }}>
            INCIDENT RESPONSE & BREACH CONTAINMENT
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Correlate related multi-stage flow alerts into formalized high-priority incident investigations
          </p>
        </div>

        <button
          onClick={() => setCreateModalOpen(true)}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white font-bold text-xs uppercase tracking-wider flex items-center space-x-2 shadow-lg shadow-rose-900/30"
        >
          <Plus className="w-4 h-4" />
          <span>Declare Security Incident</span>
        </button>
      </div>

      {/* Incidents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {incidents.map((inc) => (
          <div
            key={inc.id}
            onClick={() => openIncidentModal(inc)}
            className="glass-panel p-6 rounded-xl border border-slate-800 hover:border-slate-700 cursor-pointer transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-mono-code text-cyan-400 text-xs font-bold">{inc.incident_code}</span>
                  <h2 className="text-base font-bold text-white tracking-wide mt-1">{inc.title}</h2>
                </div>
                <SeverityBadge severity={inc.severity} />
              </div>

              <p className="text-xs text-slate-300 mt-2 line-clamp-2">{inc.description || 'No description logged.'}</p>

              {/* Scope */}
              <div className="mt-4 flex flex-wrap gap-2 text-[11px]">
                <div className="px-2 py-1 bg-slate-900 border border-slate-800 rounded text-slate-300 font-mono-code">
                  Assets: {inc.affected_assets?.length || 0}
                </div>
                <div className="px-2 py-1 bg-slate-900 border border-slate-800 rounded text-slate-300 font-mono-code">
                  IOCs: {inc.associated_iocs?.length || 0}
                </div>
                <div className="px-2 py-1 bg-slate-900 border border-slate-800 rounded text-cyan-400 font-mono-code">
                  Linked Alerts: {inc.linked_alert_count || 0}
                </div>
              </div>
            </div>

            <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
              <span className="text-slate-500">Lead: {inc.lead_analyst || 'analyst'}</span>
              <StatusBadge status={inc.status} />
            </div>
          </div>
        ))}
      </div>

      {/* Declare Incident Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Declare Security Incident"
        subtitle="Escalate coordinated attack flow telemetry into formal incident investigation"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Incident Title *</label>
            <input
              type="text"
              required
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. Distributed SYN Flood and Resource Degradation Campaign"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Severity Rating</label>
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

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Executive Summary</label>
            <textarea
              rows={3}
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="Context, impacted services, and containment hypothesis..."
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Affected Assets (Comma-separated IPs/Hosts)</label>
            <input
              type="text"
              value={newAssets}
              onChange={(e) => setNewAssets(e.target.value)}
              placeholder="10.0.0.1, 10.0.0.2"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono-code"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Associated IOCs (Comma-separated)</label>
            <input
              type="text"
              value={newIOCs}
              onChange={(e) => setNewIOCs(e.target.value)}
              placeholder="45.33.32.156, 185.220.101.5"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono-code"
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
              className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs rounded-lg uppercase tracking-wider"
            >
              Escalate & Declare
            </button>
          </div>
        </form>
      </Modal>

      {/* Incident Details & Timeline Modal */}
      {selectedIncident && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedIncident(null)}
          title={`INCIDENT DETAIL // ${selectedIncident.incident_code}`}
          subtitle={selectedIncident.title}
          maxWidth="max-w-3xl"
        >
          <div className="space-y-5">
            <div className="flex items-center justify-between p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs">
              <div>
                Severity: <SeverityBadge severity={selectedIncident.severity} />
              </div>
              <div>
                Status: <StatusBadge status={selectedIncident.status} />
              </div>
              <div className="text-slate-400">
                Lead: <strong className="text-white">{selectedIncident.lead_analyst}</strong>
              </div>
            </div>

            {/* Scope */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                <span className="font-bold text-slate-400 uppercase text-[10px]">Impacted Assets</span>
                <div className="mt-1 font-mono-code text-slate-200">{selectedIncident.affected_assets?.join(', ') || 'None listed'}</div>
              </div>
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                <span className="font-bold text-slate-400 uppercase text-[10px]">Associated IOCs</span>
                <div className="mt-1 font-mono-code text-cyan-400">{selectedIncident.associated_iocs?.join(', ') || 'None listed'}</div>
              </div>
            </div>

            {/* Incident Timeline */}
            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Investigation Timeline</h3>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {selectedIncident.timeline?.map((item, idx) => (
                  <div key={idx} className="flex items-start space-x-3 p-2 bg-slate-950 rounded border border-slate-800/80 text-xs">
                    <Clock className="w-3.5 h-3.5 text-cyan-400 mt-0.5 shrink-0" />
                    <div>
                      <div className="text-slate-300">{item.event}</div>
                      <div className="text-[10px] text-slate-500 font-mono-code">{item.user} &bull; {new Date(item.timestamp).toLocaleTimeString()}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Update Form */}
            <form onSubmit={handleUpdate} className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
              <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Update Incident Status & Log Action</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Status</label>
                  <select
                    value={updateStatus}
                    onChange={(e) => setUpdateStatus(e.target.value)}
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
                  >
                    <option value="Open">Open</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Contained">Contained</option>
                    <option value="Resolved">Resolved</option>
                    <option value="Closed">Closed</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Add Timeline Milestone</label>
                  <input
                    type="text"
                    value={newTimelineEvent}
                    onChange={(e) => setNewTimelineEvent(e.target.value)}
                    placeholder="e.g. Edge firewall blackhole confirmed"
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">Root Cause Analysis</label>
                <input
                  type="text"
                  value={rootCause}
                  onChange={(e) => setRootCause(e.target.value)}
                  placeholder="e.g. Unauthenticated RPC port exposed to WAN"
                  className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
                />
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-xs uppercase"
                >
                  Save Incident Update
                </button>
              </div>
            </form>
          </div>
        </Modal>
      )}
    </div>
  );
};
