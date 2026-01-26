import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Applied', value: 500 },
  { name: 'Phone Screen', value: 250 },
  { name: 'Interview', value: 120 },
  { name: 'Offer', value: 45 },
  { name: 'Hired', value: 35 },
];

interface RecruitmentFunnelProps {
  height?: number;
}

const RecruitmentFunnel: React.FC<RecruitmentFunnelProps> = ({ height = 300 }) => {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="name" type="category" width={100} />
        <Tooltip />
        <Bar dataKey="value" fill="#3b82f6" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default RecruitmentFunnel;
