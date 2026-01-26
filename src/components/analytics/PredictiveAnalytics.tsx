import { usePredictions } from '@/hooks/usePredictions';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import ModuleSkeleton from '../ui/ModuleSkeleton';

export function PredictiveAnalytics() {
  const { predictions, confidence, loading } = usePredictions();

  if (loading) {
    return <ModuleSkeleton />;
  }

  return (
    <div className="glass-card p-6 w-full h-full min-h-[400px]">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-xl font-black text-text-primary tracking-tight">AI Predictions</h3>
          <p className="text-xs font-bold text-text-muted uppercase tracking-wider">
            Revenue Forecast Q3-Q4
          </p>
        </div>
        <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-500 text-xs font-black uppercase tracking-widest">
          {(confidence * 100).toFixed(1)}% Confidence
        </div>
      </div>

      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={predictions} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
            <XAxis
              dataKey="month"
              stroke="var(--text-muted)"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="var(--text-muted)"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `$${value}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--bg-surface)',
                borderColor: 'var(--border-strong)',
                borderRadius: '12px',
                color: 'var(--text-primary)',
                boxShadow: 'var(--shadow-lg)',
              }}
            />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="var(--primary)"
              strokeWidth={3}
              dot={{ r: 4, fill: 'var(--primary)' }}
              activeDot={{ r: 6 }}
              name="Actual Revenue"
            />
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="var(--success)"
              strokeWidth={3}
              strokeDasharray="5 5"
              dot={{ r: 4, fill: 'var(--success)' }}
              name="AI Prediction"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 p-4 bg-surface/50 rounded-xl border border-border/50 text-xs text-text-muted">
        <strong className="text-text-primary">Insight:</strong> Based on current growth velocity,
        revenue is projected to increase by 15% in Q4 despite seasonal variance.
      </div>
    </div>
  );
}
