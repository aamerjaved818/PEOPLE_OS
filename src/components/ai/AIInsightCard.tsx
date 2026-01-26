import React from 'react';
import { ArrowUpRight, ArrowDownRight, Sparkles } from 'lucide-react';

interface AIInsightCardProps {
  title: string;
  value: string | number;
  trend?: string;
}

export const AIInsightCard: React.FC<AIInsightCardProps> = ({ title, value, trend }) => {
  const isPositive = trend?.startsWith('+');

  return (
    <div className="glass-card p-6 flex flex-col justify-between group hover-float">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-sm font-black text-text-muted uppercase tracking-wider">{title}</h3>
        <Sparkles
          size={16}
          className="text-primary opacity-50 group-hover:opacity-100 transition-opacity"
        />
      </div>
      <div>
        <div className="text-3xl font-black text-text-primary tracking-tight mb-2">
          {typeof value === 'number' ? `${value}%` : value}
        </div>
        {trend && (
          <div
            className={`flex items-center gap-1 text-xs font-bold uppercase tracking-wide ${isPositive ? 'text-emerald-500' : 'text-rose-500'}`}
          >
            {isPositive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
            <span>{trend} vs last month</span>
          </div>
        )}
      </div>
    </div>
  );
};
