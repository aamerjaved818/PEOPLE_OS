/**
 * ReportBuilder Component
 * Allows users to create custom reports with selected metrics
 */

import React, { useState } from 'react';
import './ReportBuilder.css';

interface MetricOption {
  id: string;
  name: string;
  category: 'headcount' | 'turnover' | 'recruitment' | 'payroll';
  description: string;
}

interface CustomReport {
  name: string;
  metrics: string[];
  format: 'pdf' | 'excel';
  frequency?: 'once' | 'weekly' | 'monthly';
}

const AVAILABLE_METRICS: MetricOption[] = [
  // Headcount Metrics
  {
    id: 'total_employees',
    name: 'Total Employees',
    category: 'headcount',
    description: 'Current headcount',
  },
  {
    id: 'new_hires',
    name: 'New Hires',
    category: 'headcount',
    description: 'New hires this period',
  },
  {
    id: 'avg_tenure',
    name: 'Average Tenure',
    category: 'headcount',
    description: 'Average employee tenure',
  },
  {
    id: 'by_department',
    name: 'By Department',
    category: 'headcount',
    description: 'Headcount breakdown by department',
  },
  { id: 'by_gender', name: 'By Gender', category: 'headcount', description: 'Gender distribution' },
  { id: 'by_grade', name: 'By Grade', category: 'headcount', description: 'Grade level breakdown' },

  // Turnover Metrics
  {
    id: 'turnover_rate',
    name: 'Turnover Rate',
    category: 'turnover',
    description: 'Voluntary and involuntary turnover',
  },
  {
    id: 'retention_rate',
    name: 'Retention Rate',
    category: 'turnover',
    description: 'Employee retention rate',
  },
  {
    id: 'turnover_by_dept',
    name: 'Turnover by Department',
    category: 'turnover',
    description: 'Department-level turnover analysis',
  },

  // Recruitment Metrics
  {
    id: 'open_positions',
    name: 'Open Positions',
    category: 'recruitment',
    description: 'Current job openings',
  },
  {
    id: 'pipeline_candidates',
    name: 'Pipeline Candidates',
    category: 'recruitment',
    description: 'Candidates in process',
  },
  {
    id: 'recruitment_funnel',
    name: 'Recruitment Funnel',
    category: 'recruitment',
    description: 'Conversion through stages',
  },
  {
    id: 'time_to_hire',
    name: 'Time to Hire',
    category: 'recruitment',
    description: 'Average days to fill position',
  },

  // Payroll Metrics
  {
    id: 'total_payroll',
    name: 'Total Payroll',
    category: 'payroll',
    description: 'Total payroll amount',
  },
  {
    id: 'avg_salary',
    name: 'Average Salary',
    category: 'payroll',
    description: 'Average employee salary',
  },
  {
    id: 'salary_by_designation',
    name: 'Salary by Designation',
    category: 'payroll',
    description: 'Payroll breakdown by designation',
  },
  {
    id: 'cost_per_employee',
    name: 'Cost per Employee',
    category: 'payroll',
    description: 'Monthly cost per employee',
  },
];

interface ReportBuilderProps {
  onSave?: (report: CustomReport) => void;
  isLoading?: boolean;
}

const ReportBuilder: React.FC<ReportBuilderProps> = ({ onSave, isLoading = false }) => {
  const [reportName, setReportName] = useState('');
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [format, setFormat] = useState<'pdf' | 'excel'>('pdf');
  const [frequency, setFrequency] = useState<'once' | 'weekly' | 'monthly'>('once');
  const [savedReports, setSavedReports] = useState<CustomReport[]>([]);

  const categories = ['headcount', 'turnover', 'recruitment', 'payroll'] as const;

  const toggleMetric = (metricId: string) => {
    setSelectedMetrics((prev) =>
      prev.includes(metricId) ? prev.filter((id) => id !== metricId) : [...prev, metricId]
    );
  };

  const handleSaveReport = () => {
    if (!reportName.trim()) {
      alert('Please enter a report name');
      return;
    }
    if (selectedMetrics.length === 0) {
      alert('Please select at least one metric');
      return;
    }

    const newReport: CustomReport = {
      name: reportName,
      metrics: selectedMetrics,
      format,
      frequency: frequency === 'once' ? undefined : frequency,
    };

    setSavedReports([...savedReports, newReport]);
    if (onSave) {
      onSave(newReport);
    }

    setReportName('');
    setSelectedMetrics([]);
  };

  const handleRemoveReport = (index: number) => {
    setSavedReports((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="report-builder">
      <div className="builder-section">
        <h3 className="builder-title">Create Custom Report</h3>

        <div className="builder-form">
          {/* Report Name */}
          <div className="form-group">
            <label className="form-label">Report Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., Quarterly HR Report"
              value={reportName}
              onChange={(e) => setReportName(e.target.value)}
              disabled={isLoading}
            />
          </div>

          {/* Metric Selection */}
          <div className="form-group">
            <label className="form-label">Select Metrics</label>
            <div className="metrics-selector">
              {categories.map((category) => (
                <div key={category} className="metric-category">
                  <h4 className="category-name">
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </h4>
                  <div className="metrics-list">
                    {AVAILABLE_METRICS.filter((m) => m.category === category).map((metric) => (
                      <label key={metric.id} className="metric-checkbox">
                        <input
                          type="checkbox"
                          checked={selectedMetrics.includes(metric.id)}
                          onChange={() => toggleMetric(metric.id)}
                          disabled={isLoading}
                        />
                        <span className="checkbox-text">
                          <span className="metric-name">{metric.name}</span>
                          <span className="metric-description">{metric.description}</span>
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Format Selection */}
          <div className="form-group">
            <label className="form-label">Export Format</label>
            <div className="format-options">
              <label className="radio-option">
                <input
                  type="radio"
                  name="format"
                  value="pdf"
                  checked={format === 'pdf'}
                  onChange={() => setFormat('pdf')}
                  disabled={isLoading}
                />
                <span>📄 PDF</span>
              </label>
              <label className="radio-option">
                <input
                  type="radio"
                  name="format"
                  value="excel"
                  checked={format === 'excel'}
                  onChange={() => setFormat('excel')}
                  disabled={isLoading}
                />
                <span>📊 Excel</span>
              </label>
            </div>
          </div>

          {/* Frequency Selection */}
          <div className="form-group">
            <label className="form-label">Delivery Frequency</label>
            <select
              className="form-select"
              value={frequency}
              onChange={(e) => setFrequency(e.target.value as any)}
              disabled={isLoading}
            >
              <option value="once">One-time Report</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          {/* Actions */}
          <div className="form-actions">
            <button
              className="button-save"
              onClick={handleSaveReport}
              disabled={isLoading || !reportName.trim() || selectedMetrics.length === 0}
            >
              <span className="button-icon">💾</span>
              Save Report Template
            </button>
          </div>
        </div>
      </div>

      {/* Saved Reports */}
      {savedReports.length > 0 && (
        <div className="builder-section">
          <h3 className="builder-title">Saved Report Templates</h3>
          <div className="saved-reports">
            {savedReports.map((report, index) => (
              <div key={index} className="report-card">
                <div className="report-header">
                  <h4 className="report-name">{report.name}</h4>
                  <span className="report-badge">{report.metrics.length} metrics</span>
                </div>
                <div className="report-details">
                  <span className="detail-item">
                    <span className="detail-label">Format:</span>
                    {report.format.toUpperCase()}
                  </span>
                  <span className="detail-item">
                    <span className="detail-label">Frequency:</span>
                    {report.frequency
                      ? report.frequency.charAt(0).toUpperCase() + report.frequency.slice(1)
                      : 'One-time'}
                  </span>
                </div>
                <div className="report-metrics">
                  {report.metrics.map((metricId, i) => {
                    const metric = AVAILABLE_METRICS.find((m) => m.id === metricId);
                    return metric ? (
                      <span key={i} className="metric-tag">
                        {metric.name}
                      </span>
                    ) : null;
                  })}
                </div>
                <div className="report-actions">
                  <button className="btn-generate">Generate Now</button>
                  <button className="btn-delete" onClick={() => handleRemoveReport(index)}>
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportBuilder;
