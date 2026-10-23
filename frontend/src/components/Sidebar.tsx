import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Radio,
  Search,
  BellRing,
  AlertOctagon,
  Globe2,
  Share2,
  ShieldAlert,
  Database,
  Cpu,
  Users2,
  FileText,
  Sliders,
  ChevronLeft,
  ChevronRight,
  HardDrive,
  CheckCircle2
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
  badge?: string;
  badgeColor?: string;
}

const navSections: { label: string; items: NavItem[] }[] = [
  {
    label: 'SURVEILLANCE & TRIAGE',
    items: [
      { name: 'SOC Dashboard', path: '/', icon: LayoutDashboard },
      { name: 'Live Traffic Replay', path: '/traffic', icon: Radio },
      { name: 'Flow Investigation', path: '/investigation', icon: Search },
      { name: 'Security Alerts', path: '/alerts', icon: BellRing, badge: 'Live', badgeColor: 'rose' },
      { name: 'Incident Response', path: '/incidents', icon: AlertOctagon }
    ]
  },
  {
    label: 'THREAT INTELLIGENCE',
    items: [
      { name: 'IOC & CTI Explorer', path: '/iocs', icon: Globe2 },
      { name: 'Threat Correlation', path: '/graph', icon: Share2 },
      { name: 'MITRE ATT&CK Matrix', path: '/mitre', icon: ShieldAlert }
    ]
  },
  {
    label: 'AI & COLLABORATION',
    items: [
      { name: 'Dataset Management', path: '/datasets', icon: Database },
      { name: 'Transformer Models', path: '/models', icon: Cpu },
      { name: 'Federated Learning', path: '/federated', icon: Users2, badge: 'FedAvg', badgeColor: 'cyan' }
    ]
  },
  {
    label: 'AUDIT & CONFIGURATION',
    items: [
      { name: 'Reports & STIX Export', path: '/reports', icon: FileText },
      { name: 'System & Health', path: '/settings', icon: Sliders }
    ]
  }
];

export const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`${
        collapsed ? 'w-18' : 'w-64'
      } border-r border-slate-800 bg-slate-950/70 backdrop-blur-md flex flex-col justify-between h-[calc(100vh-4rem)] sticky top-16 select-none overflow-y-auto transition-all duration-300 z-30`}
    >
      <div className="py-4 px-3 space-y-5">
        {/* Collapse toggle */}
        <div className="flex items-center justify-between px-2 pb-1">
          {!collapsed && (
            <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-widest font-mono">
              SOC OPERATIONS
            </span>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
            className="p-1 rounded-md text-slate-500 hover:text-slate-200 hover:bg-slate-900 transition-colors ml-auto"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {navSections.map((sec, idx) => (
          <div key={idx} className="space-y-1">
            {!collapsed && (
              <h3 className="px-2.5 text-[9.5px] font-black text-slate-500 uppercase tracking-wider font-mono">
                {sec.label}
              </h3>
            )}
            <div className="space-y-0.5 pt-0.5">
              {sec.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  title={collapsed ? item.name : undefined}
                  className={({ isActive }) =>
                    `flex items-center ${
                      collapsed ? 'justify-center px-2 py-2.5' : 'justify-between px-3 py-2'
                    } rounded-xl text-xs font-semibold transition-all group ${
                      isActive
                        ? 'bg-gradient-to-r from-cyan-500/15 to-blue-500/10 text-cyan-300 border-l-2 border-l-cyan-400 border-t border-r border-b border-cyan-500/20 shadow-sm shadow-cyan-500/10'
                        : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/60'
                    }`
                  }
                >
                  <div className="flex items-center space-x-2.5">
                    <item.icon className="w-4 h-4 transition-transform group-hover:scale-110 shrink-0" />
                    {!collapsed && <span>{item.name}</span>}
                  </div>
                  {!collapsed && item.badge && (
                    <span
                      className={`px-1.5 py-0.2 rounded text-[9px] font-extrabold uppercase tracking-wider font-mono border ${
                        item.badgeColor === 'cyan'
                          ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                          : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Persistence and engine status card */}
      <div className="p-3 border-t border-slate-900 bg-slate-950/60">
        {collapsed ? (
          <div className="flex justify-center" title="Platform Engine: Online">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          </div>
        ) : (
          <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80 space-y-1.5 text-[11px]">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-[10px] uppercase font-bold tracking-wider">Engine Status</span>
              <span className="flex items-center text-[10px] text-emerald-400 font-mono font-bold">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1"></span>
                ONLINE
              </span>
            </div>
            <div className="text-[10px] text-slate-300 flex items-center justify-between font-mono">
              <span>Model:</span>
              <span className="text-cyan-400">FlowTransformer v1</span>
            </div>
            <div className="text-[10px] text-slate-400 flex items-center justify-between font-mono">
              <span>Storage:</span>
              <span className="text-slate-300">SQLite (WAL Mode)</span>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
