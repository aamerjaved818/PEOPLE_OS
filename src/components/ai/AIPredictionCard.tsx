import React from 'react';
import { AlertCircle, ShieldCheck } from 'lucide-react';

interface AIPredictionCardProps {
  title: string;
  value: string;
  action?: string;
}

export const AIPredictionCard: React.FC<AIPredictionCardProps> = ({ title, value, action }) => {
  const isRisk = value === 'High' || value === 'Critical';

  return (
    <div
      className={`glass-card p-6 flex flex-col justify-between group hover-float relative overflow-hidden`}
    >
      {isRisk && <div className="absolute inset-0 bg-red-500/5 pointer-events-none" />}

      <div className="flex justify-between items-start mb-4 relative z-10">
        <h3 className="text-sm font-black text-text-muted uppercase tracking-wider">{title}</h3>
        {isRisk ? (
          <AlertCircle size={16} className="text-red-500 animate-pulse" />
        ) : (
          <ShieldCheck size={16} className="text-emerald-500" />
        )}
      </div>

      <div className="relative z-10">
        <div
          className={`text-2xl font-black tracking-tight mb-3 ${isRisk ? 'text-red-500' : 'text-text-primary'}`}
        >
          {value}
        </div>
        {action && (
          <div className="bg-surface/50 rounded-lg p-3 border border-border/50 backdrop-blur-sm">
            <p className="text-[0.6rem] uppercase tracking-widest text-text-muted mb-1">
              Recommended Action
            </p>
            <p className="text-xs font-bold text-text-primary">{action}</p>
          </div>
        )}
      </div>
    </div>
  );
};
