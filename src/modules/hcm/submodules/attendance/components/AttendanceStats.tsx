import React from 'react';
import { User, Clock, AlertTriangle, Zap, LucideIcon } from 'lucide-react';

interface Stat {
  label: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'neutral';
  icon: LucideIcon;
  color: string;
}

const stats: Stat[] = [
  {
    label: 'Present Employees',
    value: '238',
    change: '+2',
    trend: 'up',
    icon: User,
    color: 'primary',
  },
  {
    label: 'Late Arrivals',
    value: '12',
    change: '-5',
    trend: 'down',
    icon: Clock,
    color: 'warning',
  },
  {
    label: 'Missing Out-Time',
    value: '4',
    change: '+1',
    trend: 'up',
    icon: AlertTriangle,
    color: 'destructive',
  },
  {
    label: 'Shift Coverage',
    value: '98.2%',
    change: 'Stable',
    trend: 'neutral',
    icon: Zap,
    color: 'success',
  },
];

export const AttendanceStats: React.FC = () => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {stats.map((s, i) => (
        <div
          key={i}
          className="bg-surface p-4 rounded-md border border-border shadow-sm relative overflow-hidden group hover:shadow-md transition-all"
        >
          <div
            className={`absolute -right-3 -bottom-3 w-16 h-16 bg-${s.color}-soft blur-2xl rounded-full group-hover:scale-150 transition-transform duration-1000`}
          ></div>
          <div className="flex items-center justify-between mb-3">
            <div className={`p-2 rounded-md bg-${s.color}-soft text-${s.color}`}>
              <s.icon size={14} />
            </div>
            <span
              className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${s.trend === 'up' ? 'text-success bg-success-soft border-success/10' : s.trend === 'down' ? 'text-danger bg-danger-soft border-danger/10' : 'text-text-muted bg-muted-bg border-border'}`}
            >
              {s.change}
            </span>
          </div>
          <p className="text-[9px] font-bold text-text-muted uppercase tracking-wider mb-1">
            {s.label}
          </p>
          <h4 className="text-xl font-black text-text-primary tracking-tight">{s.value}</h4>
        </div>
      ))}
    </div>
  );
};
