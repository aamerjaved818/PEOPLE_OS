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

const data = [
  { name: 'Jan', sales: 4000, recruitment: 2400, performance: 2400 },
  { name: 'Feb', sales: 3000, recruitment: 1398, performance: 2210 },
  { name: 'Mar', sales: 2000, recruitment: 9800, performance: 2290 },
  { name: 'Apr', sales: 2780, recruitment: 3908, performance: 2000 },
  { name: 'May', sales: 1890, recruitment: 4800, performance: 2181 },
  { name: 'Jun', sales: 2390, recruitment: 3800, performance: 2500 },
];

interface TrendChartProps {
  height?: number;
}

const TrendChart: React.FC<TrendChartProps> = ({ height = 300 }) => {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="sales" stroke="#3b82f6" />
        <Line type="monotone" dataKey="recruitment" stroke="#10b981" />
        <Line type="monotone" dataKey="performance" stroke="#f59e0b" />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TrendChart;
