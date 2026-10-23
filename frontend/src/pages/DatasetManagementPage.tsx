import React, { useState, useEffect } from 'react';
import { Database, Upload, CheckCircle2, AlertCircle, FileText, BarChart2 } from 'lucide-react';
import { api } from '../services/api';
import { Dataset } from '../types/api';
import { Modal } from '../components/Modal';

export const DatasetManagementPage: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [uploadModalOpen, setUploadModalOpen] = useState<boolean>(false);
  const [inspectDataset, setInspectDataset] = useState<Dataset | null>(null);

  // Upload Form State
  const [uploadName, setUploadName] = useState('');
  const [uploadDesc, setUploadDesc] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      setLoading(true);
      const data = await api.getDatasets();
      setDatasets(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !uploadName) {
      setUploadError('Please specify a dataset name and select a CSV file.');
      return;
    }
    setUploading(true);
    setUploadError(null);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('name', uploadName);
      formData.append('description', uploadDesc);
      await api.uploadDataset(formData);
      setUploadModalOpen(false);
      setUploadName('');
      setUploadDesc('');
      setSelectedFile(null);
      await loadDatasets();
    } catch (err: any) {
      setUploadError(err.message || 'Dataset upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-black text-white tracking-wide" style={{ fontFamily: 'var(--font-display)' }}>
            RESEARCH DATASETS & INGESTION ADAPTERS
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Primary: <strong className="text-cyan-400">BigFlow-NIDS-V2</strong> (66.9M NetFlow telemetry flows across 67 Parquet partitions) & multi-dataset research adapters
          </p>
        </div>

        <button
          onClick={() => setUploadModalOpen(true)}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs uppercase tracking-wider flex items-center space-x-2 shadow-lg shadow-cyan-500/20"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Dataset (CSV/Parquet)</span>
        </button>
      </div>

      {/* Dataset Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {datasets.map((ds) => (
          <div key={ds.id} className={`glass-panel p-6 rounded-xl border flex flex-col justify-between ${ds.adapter_type === 'BigFlow-NIDS-V2' ? 'border-cyan-500/40 bg-slate-900/40 shadow-lg shadow-cyan-950/30' : 'border-slate-800'}`}>
            <div>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-base font-bold text-white tracking-wide">{ds.name}</h2>
                    {ds.adapter_type === 'BigFlow-NIDS-V2' ? (
                      <span className="px-2 py-0.5 text-[9px] font-black bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 rounded uppercase shadow-sm shadow-cyan-500/20">
                        Primary Dataset
                      </span>
                    ) : ds.is_sample && (
                      <span className="px-1.5 py-0.5 text-[9px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded uppercase">
                        Sample Fixture
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{ds.description || 'No description provided.'}</p>
                </div>
                <div className={`p-2.5 border rounded-lg ${ds.adapter_type === 'BigFlow-NIDS-V2' ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400' : 'bg-slate-900 border-slate-800 text-slate-400'}`}>
                  <Database className="w-5 h-5" />
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-3 gap-3 my-5 p-3 rounded-lg bg-slate-950/60 border border-slate-900">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase font-semibold">Total Records</span>
                  <div className="text-sm font-bold font-mono-code text-slate-200 mt-0.5">
                    {ds.total_rows.toLocaleString()}
                  </div>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase font-semibold">Benign Flows</span>
                  <div className="text-sm font-bold font-mono-code text-emerald-400 mt-0.5">
                    {ds.benign_count.toLocaleString()}
                  </div>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 uppercase font-semibold">Malicious Flows</span>
                  <div className="text-sm font-bold font-mono-code text-rose-400 mt-0.5">
                    {ds.malicious_count.toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Adapter & Validation Info */}
              <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
                <div>
                  Adapter: <strong className="text-cyan-400 font-mono-code">{ds.adapter_type}</strong>
                </div>
                <div>
                  Features: <strong className="text-slate-300 font-mono-code">{ds.total_columns} columns</strong>
                </div>
                {ds.adapter_type === 'BigFlow-NIDS-V2' && (
                  <div>
                    Format: <strong className="text-emerald-400 font-mono-code">67 Parquet Partitions (2.83 GB)</strong>
                  </div>
                )}
              </div>
              <div className="text-[11px] text-slate-500 mt-2 truncate font-mono-code">
                Path: {ds.file_path}
              </div>
            </div>

            <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[11px] text-slate-500">
                Validated: {ds.is_validated ? 'Schema Passed' : 'Pending'}
              </span>
              <button
                onClick={() => setInspectDataset(ds)}
                className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-200 rounded-lg flex items-center space-x-1.5 transition-colors"
              >
                <BarChart2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Inspect Class Distribution</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Upload Modal */}
      <Modal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        title="Upload NetFlow Dataset CSV"
        subtitle="Automatic adapter detection for NF-UNSW-NB15-v2, NF-BoT-IoT-v2, Edge-IIoTset, or generic formats"
      >
        <form onSubmit={handleUpload} className="space-y-4">
          {uploadError && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-lg">
              {uploadError}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Dataset Tag Name *</label>
            <input
              type="text"
              required
              value={uploadName}
              onChange={(e) => setUploadName(e.target.value)}
              placeholder="e.g. Edge_IIoTset_Evaluation"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Description</label>
            <textarea
              rows={2}
              value={uploadDesc}
              onChange={(e) => setUploadDesc(e.target.value)}
              placeholder="Notes on capture time, protocol scope, or attack scenarios..."
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">CSV File *</label>
            <input
              type="file"
              accept=".csv"
              required
              onChange={(e) => setSelectedFile(e.target.files ? e.target.files[0] : null)}
              className="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-cyan-500/10 file:text-cyan-400 hover:file:bg-cyan-500/20"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => setUploadModalOpen(false)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={uploading}
              className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs rounded-lg uppercase tracking-wider"
            >
              {uploading ? 'Parsing & Adapting...' : 'Upload & Validate'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Inspect Class Distribution Modal */}
      {inspectDataset && (
        <Modal
          isOpen={true}
          onClose={() => setInspectDataset(null)}
          title={`Schema & Distribution // ${inspectDataset.name}`}
          subtitle={`Adapter: ${inspectDataset.adapter_type} | Total Rows: ${inspectDataset.total_rows}`}
        >
          <div className="space-y-4">
            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Class Frequency</h3>
              <div className="space-y-2">
                {Object.entries(inspectDataset.class_distribution || {}).map(([cls, cnt]) => {
                  const pct = Math.round((cnt / (inspectDataset.total_rows || 1)) * 100);
                  return (
                    <div key={cls} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-semibold text-slate-300">{cls}</span>
                        <span className="font-mono-code text-slate-400">{cnt} flows ({pct}%)</span>
                      </div>
                      <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                        <div className="bg-cyan-500 h-1.5 rounded-full" style={{ width: `${pct}%` }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setInspectDataset(null)}
                className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
