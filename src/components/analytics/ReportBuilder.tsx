import React, { useState } from 'react';
import { Plus, CheckCircle } from 'lucide-react';

interface Metric {
  id: string;
  name: string;
  label: string;
  selected: boolean;
}

interface ReportBuilderProps {
  onBuild?: (metrics: string[]) => void;
}

const allMetrics: Metric[] = [
  { id: '1', name: 'Total Revenue', label: 'Total Revenue', selected: false },
  { id: '2', name: 'Sales Growth', label: 'YoY Sales Growth', selected: false },
  { id: '3', name: 'Pipeline', label: 'Sales Pipeline', selected: false },
  { id: '4', name: 'Win Rate', label: 'Sales Win Rate', selected: false },
  { id: '5', name: 'Avg Deal Size', label: 'Average Deal Size', selected: false },
  { id: '6', name: 'Time to Hire', label: 'Time to Hire', selected: false },
  { id: '7', name: 'Offer Accept', label: 'Offer Acceptance Rate', selected: false },
  { id: '8', name: 'Cost Per Hire', label: 'Cost Per Hire', selected: false },
  { id: '9', name: 'Employee Count', label: 'Total Employees', selected: false },
  { id: '10', name: 'Turnover Rate', label: 'Employee Turnover Rate', selected: false },
  { id: '11', name: 'Avg Salary', label: 'Average Salary', selected: false },
  { id: '12', name: 'Performance Score', label: 'Performance Score', selected: false },
  {
    id: '13',
    name: 'Engagement Score',
    label: 'Employee Engagement Score',
    selected: false,
  },
  { id: '14', name: 'Training Hours', label: 'Training Hours per Employee', selected: false },
];

const ReportBuilder: React.FC<ReportBuilderProps> = ({ onBuild }) => {
  const [metrics, setMetrics] = useState<Metric[]>(allMetrics);
  const [reportName, setReportName] = useState('');
  const [reportFormat, setReportFormat] = useState('pdf');

  const toggleMetric = (id: string) => {
    setMetrics((prev) => prev.map((m) => (m.id === id ? { ...m, selected: !m.selected } : m)));
  };

  const clearAll = () => {
    setMetrics((prev) => prev.map((m) => ({ ...m, selected: false })));
  };

  const selectAll = () => {
    setMetrics((prev) => prev.map((m) => ({ ...m, selected: true })));
  };

  const handleBuild = () => {
    const selectedMetricIds = metrics.filter((m) => m.selected).map((m) => m.name);

    if (selectedMetricIds.length === 0) {
      alert('Please select at least one metric');
      return;
    }

    if (!reportName.trim()) {
      alert('Please enter a report name');
      return;
    }

    onBuild?.(selectedMetricIds);
    alert(`Report "${reportName}" queued for generation`);
  };

  const selectedCount = metrics.filter((m) => m.selected).length;

  return (
    <div className="space-y-6">
      {/* Form Section */}
      <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Report Details</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Report Name</label>
            <input
              type="text"
              value={reportName}
              onChange={(e) => setReportName(e.target.value)}
              placeholder="e.g., Q1 Executive Summary"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Format</label>
            <select
              value={reportFormat}
              onChange={(e) => setReportFormat(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
              <option value="html">HTML</option>
            </select>
          </div>
        </div>
      </div>

      {/* Metrics Selection */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Select Metrics ({selectedCount}/{metrics.length})
            </h3>
            <p className="text-sm text-gray-600">Choose the metrics to include in your report</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={selectAll}
              className="text-sm px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition"
            >
              Select All
            </button>
            <button
              onClick={clearAll}
              className="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {metrics.map((metric) => (
            <button
              key={metric.id}
              onClick={() => toggleMetric(metric.id)}
              className={`p-4 rounded-lg border-2 transition text-left ${
                metric.selected
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{metric.label}</p>
                  <p className="text-xs text-gray-500 mt-1">{metric.name}</p>
                </div>
                {metric.selected && (
                  <CheckCircle className="text-blue-600 flex-shrink-0 ml-2" size={20} />
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          onClick={handleBuild}
          disabled={selectedCount === 0 || !reportName.trim()}
          className="flex items-center gap-2 flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed justify-center"
        >
          <Plus size={20} />
          Generate Report
        </button>
      </div>
    </div>
  );
};

export default ReportBuilder;
