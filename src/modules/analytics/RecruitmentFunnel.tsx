import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { PALETTE } from '@/theme/palette';
import { Users } from 'lucide-react';

interface RecruitmentFunnelProps {
  data: any[];
}

const RecruitmentFunnel: React.FC<RecruitmentFunnelProps> = ({ data }) => {
  const COLORS = [
    'hsl(var(--primary))',
    'hsl(var(--primary-soft))',
    'hsl(var(--secondary))',
    'hsl(var(--success))',
    'hsl(var(--warning))',
  ];

  return (
    <div
      role="region"
      aria-label="Recruitment Funnel"
      className="bg-card rounded-[2rem] p-10 border border-border shadow-2xl space-y-8"
    >
      <div className="flex items-center gap-6">
        <div className="w-14 h-14 bg-emerald-500/10 rounded-2xl flex items-center justify-center shadow-lg shadow-emerald-500/10">
          <Users className="text-emerald-600" size={28} />
        </div>
        <div>
          <h3 className="text-2xl font-black text-slate-900 dark:text-white uppercase tracking-tighter">
            Recruitment Funnel
          </h3>
          <p className="text-[0.625rem] font-black text-slate-400 uppercase tracking-widest mt-1">
            Candidate Pipeline Distribution
          </p>
        </div>
      </div>

      <div className="h-[25rem] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={data}
            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              horizontal={true}
              vertical={false}
              stroke={PALETTE.grid}
            />
            <XAxis type="number" hide />
            <YAxis
              dataKey="name"
              type="category"
              axisLine={false}
              tickLine={false}
              tick={{ fill: PALETTE.axis, fontSize: 11, fontWeight: 900 }}
            />
            <Tooltip
              cursor={{ fill: 'transparent' }}
              contentStyle={{
                backgroundColor: PALETTE.tooltipBg,
                border: 'none',
                borderRadius: '1rem',
                color: PALETTE.tooltipText,
                fontSize: '0.75rem',
                fontWeight: 'bold',
              }}
            />
            <Bar dataKey="value" radius={[0, 10, 10, 0]} barSize={40}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="pt-4 border-t border-border flex justify-between items-center">
        <div className="flex items-center gap-3">
          <span className="text-[0.625rem] font-black text-slate-400 uppercase tracking-widest">
            Total Candidates
          </span>
          <span className="text-lg font-black text-slate-900 dark:text-white">
            {data.reduce((acc, curr) => acc + curr.value, 0)}
          </span>
        </div>
        <button className="text-[0.625rem] font-black text-primary uppercase tracking-widest hover:underline">
          View ATS Details
        </button>
      </div>
    </div>
  );
};

export default RecruitmentFunnel;
