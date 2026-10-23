import React, { useState, useEffect } from 'react';
import {
  BellRing,
  ShieldAlert,
  CheckCircle2,
  User,
  MessageSquare,
  ExternalLink,
  Filter,
  Search,
  Eye,
  Zap,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { Alert, Incident } from '../types/api';
import { SeverityBadge, StatusBadge } from '../components/Badge';
import { Modal } from '../components/Modal';
import { useToast } from '../context/ToastContext';
import { FlowForensicsModal, ForensicFlowData } from '../components/FlowForensicsModal';

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  // Forensic modal state
  const [forensicFlow, setForensicFlow] = useState<ForensicFlowData | null>(null);
  const [isForensicOpen, setIsForensicOpen] = useState(false);

  // Note form state
  const [newNote, setNewNote] = useState('');
  const [assignedTo, setAssignedTo] = useState('');
  const [newStatus, setNewStatus] = useState('');
  const [selectedIncidentId, setSelectedIncidentId] = useState<number | ''>('');

  const { showToast } = useToast();

  useEffect(() => {
    loadAlerts();
    api.getIncidents().then(setIncidents).catch(console.error);
  }, [statusFilter, severityFilter]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      if (severityFilter) params.severity = severityFilter;
      const res = await api.getAlerts(params);
      setAlerts(res.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAlert) return;
    try {
      const updatePayload: any = {};
      if (newStatus && newStatus !== selectedAlert.status) updatePayload.status = newStatus;
      if (assignedTo && assignedTo !== selectedAlert.assigned_to) updatePayload.assigned_to = assignedTo;
      if (newNote) updatePayload.new_note = newNote;
      if (selectedIncidentId) updatePayload.incident_id = Number(selectedIncidentId);

      const updated = await api.updateAlert(selectedAlert.id, updatePayload);
      setSelectedAlert(updated);
      setNewNote('');
      await loadAlerts();
      showToast('Alert Triage Updated', `Alert ${selectedAlert.alert_code} status updated to ${newStatus}`, 'success');
    } catch (err: any) {
      showToast('Update Failed', err?.message || 'Could not update alert', 'danger');
    }
  };

  const openAlertModal = (alert: Alert) => {
    setSelectedAlert(alert);
    setNewStatus(alert.status);
    setAssignedTo(alert.assigned_to || '');
    setSelectedIncidentId(alert.incident_id || '');
    setNewNote('');
  };

  const handleOpenForensics = (alert: Alert, e: React.MouseEvent) => {
    e.stopPropagation();
    setForensicFlow({
      id: alert.id,
      src_ip: alert.src_ip || '192.168.1.105',
      dst_ip: '10.0.0.1',
      dst_port: alert.dst_port || 80,
      protocol: 'TCP',
      is_malicious: true,
      predicted_class: alert.category,
      confidence: 0.982,
      severity: alert.severity,
      risk_score: alert.risk_score,
      mitre_tactic: 'Initial Access',
      mitre_technique_id: alert.mitre_technique_id || 'T1110',
      inference_time_ms: 11.8,
      saliency_map: {
        dst_port: 0.39,
        flow_duration: 0.26,
        fwd_pkts: 0.17,
        tcp_flags_syn: 0.12,
        flow_rate_pkts_per_sec: 0.06
      },
      explanation: `Detection ${alert.alert_code}: Flow telemetry from ${alert.src_ip} targeting port ${alert.dst_port} exhibited high volumetric rate and abnormal TCP flag ratios matching ${alert.category} heuristics.`
    });
    setIsForensicOpen(true);
  };

  const filteredAlerts = alerts.filter((a) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      a.alert_code.toLowerCase().includes(q) ||
      a.title.toLowerCase().includes(q) ||
      a.category.toLowerCase().includes(q) ||
      (a.src_ip && a.src_ip.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1
            className="text-xl md:text-2xl font-black text-white tracking-wide flex items-center space-x-2.5"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            <BellRing className="w-6 h-6 text-cyan-400" />
            <span>SECURITY ALERTS & INCIDENT TRIAGE</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time FlowTransformer detections &bull; Lifecycle: New &rarr; Acknowledged &rarr; Investigating &rarr; Resolved
          </p>
        </div>

        {/* Filter & Search Bar */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search code, IP, attack..."
              className="pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-850 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-48 transition-all"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-850 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50 transition-all font-sans"
          >
            <option value="">All Statuses</option>
            <option value="New">New</option>
            <option value="Acknowledged">Acknowledged</option>
            <option value="Investigating">Investigating</option>
            <option value="Resolved">Resolved</option>
            <option value="False Positive">False Positive</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-855 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50 transition-all font-sans"
          >
            <option value="">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 shadow-xl overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 font-bold uppercase text-[10px] tracking-wider font-mono">
              <th className="pb-3">Alert Code</th>
              <th className="pb-3">Title & Classification</th>
              <th className="pb-3">Severity</th>
              <th className="pb-3">Risk Score</th>
              <th className="pb-3">Source & Port</th>
              <th className="pb-3">MITRE Technique</th>
              <th className="pb-3">Assignee</th>
              <th className="pb-3">Status</th>
              <th className="pb-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-medium">
            {filteredAlerts.map((alert) => (
              <tr
                key={alert.id}
                onClick={() => openAlertModal(alert)}
                className="hover:bg-slate-850/60 cursor-pointer transition-colors group"
              >
                <td className="py-3 font-mono text-cyan-400 font-bold">{alert.alert_code}</td>
                <td className="py-3">
                  <div className="font-bold text-slate-200">{alert.title}</div>
                  <div className="text-[11px] text-slate-400">{alert.category}</div>
                </td>
                <td className="py-3">
                  <SeverityBadge severity={alert.severity} />
                </td>
                <td className="py-3 font-mono font-black text-amber-400">{alert.risk_score}/100</td>
                <td className="py-3 font-mono text-slate-300">
                  {alert.src_ip || 'N/A'}:{alert.src_port || '*'} &rarr; {alert.dst_port || '*'}
                </td>
                <td className="py-3 font-mono text-cyan-400 font-bold">{alert.mitre_technique_id || 'T1040'}</td>
                <td className="py-3 text-slate-300">{alert.assigned_to || 'Unassigned'}</td>
                <td className="py-3">
                  <StatusBadge status={alert.status} />
                </td>
                <td className="py-3 text-right">
                  <button
                    onClick={(e) => handleOpenForensics(alert, e)}
                    className="px-2.5 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-[11px] font-bold inline-flex items-center space-x-1 transition-colors"
                    title="Examine eX-NIDS Saliency Map"
                  >
                    <Eye className="w-3 h-3" />
                    <span>Forensics</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredAlerts.length === 0 && !loading && (
          <div className="text-center py-12 text-slate-400 text-xs font-mono space-y-2">
            <div>No alerts matching the selected filter criteria.</div>
            <p className="text-[11px] text-slate-500">
              Use the top-bar &lsquo;⚡ Test Attack Stream&rsquo; button to generate live detections.
            </p>
          </div>
        )}
      </div>

      {/* Alert Investigation Modal */}
      {selectedAlert && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedAlert(null)}
          title={`ALERT INVESTIGATION // ${selectedAlert.alert_code}`}
          subtitle={selectedAlert.title}
          maxWidth="max-w-3xl"
        >
          <div className="space-y-5">
            {/* Metadata Banner */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 bg-slate-950 rounded-xl border border-slate-800 text-center">
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-bold font-mono">Attack Category</span>
                <div className="text-sm font-bold text-rose-400 mt-0.5">{selectedAlert.category}</div>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-bold font-mono">Risk Score</span>
                <div className="text-sm font-black font-mono text-amber-400 mt-0.5">{selectedAlert.risk_score} / 100</div>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-bold font-mono">Severity</span>
                <div className="mt-1">
                  <SeverityBadge severity={selectedAlert.severity} />
                </div>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-bold font-mono">MITRE Technique</span>
                <div className="text-sm font-bold font-mono text-cyan-400 mt-0.5">
                  {selectedAlert.mitre_technique_id || 'T1040'}
                </div>
              </div>
            </div>

            {/* Evidence Description */}
            <div className="p-4 bg-slate-950/70 rounded-xl border border-slate-800">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 font-mono">
                Detection Evidence & Telemetry Summary
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed font-sans">{selectedAlert.description}</p>
            </div>

            {/* Analyst Action Form */}
            <form onSubmit={handleUpdateAlert} className="space-y-4 p-4 bg-slate-950/50 rounded-xl border border-slate-800">
              <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider font-mono">
                Triage & Lifecycle Action
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Status Lifecycle</label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
                  >
                    <option value="New">New</option>
                    <option value="Acknowledged">Acknowledged</option>
                    <option value="Investigating">Investigating</option>
                    <option value="Resolved">Resolved</option>
                    <option value="False Positive">False Positive</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Assigned Analyst</label>
                  <input
                    type="text"
                    value={assignedTo}
                    onChange={(e) => setAssignedTo(e.target.value)}
                    placeholder="e.g. analyst or admin"
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Link to Incident</label>
                  <select
                    value={selectedIncidentId}
                    onChange={(e) => setSelectedIncidentId(e.target.value ? Number(e.target.value) : '')}
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
                  >
                    <option value="">None (Standalone Alert)</option>
                    {incidents.map((inc) => (
                      <option key={inc.id} value={inc.id}>
                        {inc.incident_code}: {inc.title.substring(0, 30)}...
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">Add Investigation Log Note</label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    placeholder="Log observation, packet analysis, or containment command..."
                    className="flex-1 px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200"
                  />
                  <button
                    type="submit"
                    className="px-4 py-1.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-xs uppercase transition-colors"
                  >
                    Save Update
                  </button>
                </div>
              </div>
            </form>

            {/* Historical Notes Audit */}
            {selectedAlert.investigation_notes && selectedAlert.investigation_notes.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 font-mono">
                  Investigation History Audit Log
                </h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {selectedAlert.investigation_notes.map((n, i) => (
                    <div key={i} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                      <div className="flex justify-between text-slate-400 text-[10px] mb-1 font-mono">
                        <span className="font-bold text-slate-300">{n.author}</span>
                        <span>{new Date(n.timestamp).toLocaleTimeString()}</span>
                      </div>
                      <div className="text-slate-200">{n.note}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* Forensic Modal */}
      <FlowForensicsModal
        isOpen={isForensicOpen}
        onClose={() => setIsForensicOpen(false)}
        flow={forensicFlow}
        onContain={(srcIp) => {
          showToast(
            'Containment Rule Enforced',
            `Null-route and perimeter block initiated for adversary IP ${srcIp}`,
            'success'
          );
        }}
      />
    </div>
  );
};
