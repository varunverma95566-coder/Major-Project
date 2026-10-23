import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ElementType;
  trend?: string;
  isPositive?: boolean;
  glowColor?: 'cyan' | 'rose' | 'emerald' | 'purple';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  isPositive = true,
  glowColor = 'cyan'
}) => {
  const glowStyles = {
    cyan: 'border-slate-800/80 hover:border-cyan-500/50 hover:shadow-cyan-500/15',
    rose: 'border-slate-800/80 hover:border-rose-500/50 hover:shadow-rose-500/15',
    emerald: 'border-slate-800/80 hover:border-emerald-500/50 hover:shadow-emerald-500/15',
    purple: 'border-slate-800/80 hover:border-purple-500/50 hover:shadow-purple-500/15'
  };

  const iconColors = {
    cyan: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30 shadow-cyan-500/10',
    rose: 'bg-rose-500/15 text-rose-400 border-rose-500/30 shadow-rose-500/10',
    emerald: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30 shadow-emerald-500/10',
    purple: 'bg-purple-500/15 text-purple-400 border-purple-500/30 shadow-purple-500/10'
  };

  const accentBars = {
    cyan: 'from-cyan-500 to-blue-500',
    rose: 'from-rose-500 to-amber-500',
    emerald: 'from-emerald-500 to-teal-500',
    purple: 'from-purple-500 to-indigo-500'
  };

  return (
    <div
      className={`relative overflow-hidden rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border p-5 transition-all duration-300 shadow-lg ${glowStyles[glowColor]} group backdrop-blur-md`}
    >
      {/* Top accent glow line */}
      <div
        className={`absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r ${accentBars[glowColor]} opacity-70 group-hover:opacity-100 transition-opacity`}
      ></div>

      <div className="flex items-start justify-between">
        <div className="flex-1 pr-3">
          <p className="text-[10.5px] font-bold text-slate-400 tracking-wider uppercase font-mono">
            {title}
          </p>
          <div className="mt-2 flex items-baseline space-x-2">
            <span
              className="text-2xl font-black text-white tracking-tight font-mono"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              {value}
            </span>
            {trend && (
              <span
                className={`inline-flex items-center text-[10.5px] font-bold font-mono px-1.5 py-0.5 rounded ${
                  isPositive
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                }`}
              >
                {isPositive ? (
                  <TrendingUp className="w-3 h-3 mr-1" />
                ) : (
                  <TrendingDown className="w-3 h-3 mr-1" />
                )}
                {trend}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="mt-1.5 text-[11px] text-slate-400 font-medium leading-tight">
              {subtitle}
            </p>
          )}
        </div>

        <div
          className={`w-11 h-11 rounded-xl flex items-center justify-center border shadow-md transition-transform group-hover:scale-105 shrink-0 ${iconColors[glowColor]}`}
        >
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
};
