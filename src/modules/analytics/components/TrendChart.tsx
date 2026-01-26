/**
 * TrendChart Component
 * Displays headcount trends with Recharts
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import './TrendChart.css';

interface TrendDataPoint {
  name: string;
  count: number;
  liability: number;
}

interface TrendChartProps {
  data: TrendDataPoint[];
  title?: string;
  showLiability?: boolean;
}

const TrendChart: React.FC<TrendChartProps> = ({
  data,
  title = 'Headcount Trend',
  showLiability = true,
}) => {
  return (
    <div className="trend-chart-container">
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="name" stroke="#6b7280" style={{ fontSize: '12px' }} />
            <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
              }}
              formatter={(value) => `${value}`}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#1e40af"
              strokeWidth={2}
              dot={{ fill: '#1e40af', r: 4 }}
              activeDot={{ r: 6 }}
              name="Employee Count"
            />
            {showLiability && (
              <Line
                type="monotone"
                dataKey="liability"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={{ fill: '#f59e0b', r: 4 }}
                activeDot={{ r: 6 }}
                name="Gratuity Liability"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-summary">
        <div className="summary-item">
          <span className="label">Current</span>
          <span className="value">{data[data.length - 1]?.count || 0}</span>
        </div>
        <div className="summary-item">
          <span className="label">Previous</span>
          <span className="value">{data[data.length - 2]?.count || 0}</span>
        </div>
        <div className="summary-item">
          <span className="label">Change</span>
          <span
            className={`value ${(data[data.length - 1]?.count || 0) >= (data[data.length - 2]?.count || 0) ? 'positive' : 'negative'}`}
          >
            {(
              (data[data.length - 1]?.count || 0) - (data[data.length - 2]?.count || 0)
            ).toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
};

export default TrendChart;
