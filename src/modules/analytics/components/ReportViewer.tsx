/**
 * ReportViewer Component
 * Displays and manages previously generated reports
 */

import React, { useState, useEffect } from 'react';
import './ReportViewer.css';

interface GeneratedReport {
  id: string;
  name: string;
  type: 'workforce' | 'recruitment' | 'payroll' | 'custom';
  format: 'pdf' | 'excel';
  createdAt: string;
  fileSize: number;
  downloadUrl: string;
}

interface ReportViewerProps {
  isLoading?: boolean;
  onDelete?: (reportId: string) => void;
}

const ReportViewer: React.FC<ReportViewerProps> = ({ isLoading = false, onDelete }) => {
  const [reports, setReports] = useState<GeneratedReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<GeneratedReport | null>(null);
  const [loadingReports, setLoadingReports] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoadingReports(true);
        const response = await fetch('/api/v1/analytics/reports', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token') || ''}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch reports');
        }

        const data = await response.json();
        setReports(data.reports || []);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load reports');
        console.error('Error fetching reports:', err);
      } finally {
        setLoadingReports(false);
      }
    };

    fetchReports();
  }, []);

  const handleDownload = async (report: GeneratedReport) => {
    try {
      const response = await fetch(report.downloadUrl, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
      });

      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${report.name}.${report.format === 'pdf' ? 'pdf' : 'xlsx'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download error:', err);
      setError('Failed to download report');
    }
  };

  const handleDelete = async (reportId: string) => {
    if (!window.confirm('Are you sure you want to delete this report?')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/analytics/reports/${reportId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete report');
      }

      setReports((prev) => prev.filter((r) => r.id !== reportId));
      if (selectedReport?.id === reportId) {
        setSelectedReport(null);
      }
      if (onDelete) {
        onDelete(reportId);
      }
    } catch (err) {
      console.error('Delete error:', err);
      setError('Failed to delete report');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) {
      return '0 B';
    }
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loadingReports) {
    return (
      <div className="report-viewer">
        <div className="viewer-loading">Loading reports...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="report-viewer">
        <div className="viewer-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="report-viewer">
      <div className="viewer-header">
        <h3>Report History</h3>
        <span className="report-count">{reports.length} reports</span>
      </div>

      {reports.length === 0 ? (
        <div className="no-reports">
          <span className="icon">📭</span>
          <p>No reports generated yet</p>
          <p className="subtitle">Generate your first report to see it here</p>
        </div>
      ) : (
        <div className="viewer-content">
          <div className="reports-list">
            {reports.map((report) => (
              <div
                key={report.id}
                className={`report-item ${selectedReport?.id === report.id ? 'selected' : ''}`}
                onClick={() => setSelectedReport(report)}
              >
                <div className="item-icon">{report.format === 'pdf' ? '📄' : '📊'}</div>
                <div className="item-info">
                  <h4 className="item-name">{report.name}</h4>
                  <p className="item-meta">
                    <span className="meta-type">{report.type}</span>
                    <span className="meta-date">{formatDate(report.createdAt)}</span>
                    <span className="meta-size">{formatFileSize(report.fileSize)}</span>
                  </p>
                </div>
              </div>
            ))}
          </div>

          {selectedReport && (
            <div className="report-detail">
              <div className="detail-header">
                <h3>{selectedReport.name}</h3>
                <button className="detail-close" onClick={() => setSelectedReport(null)}>
                  ✕
                </button>
              </div>

              <div className="detail-info">
                <div className="info-group">
                  <span className="info-label">Type</span>
                  <span className="info-value">{selectedReport.type}</span>
                </div>
                <div className="info-group">
                  <span className="info-label">Format</span>
                  <span className="info-value">{selectedReport.format.toUpperCase()}</span>
                </div>
                <div className="info-group">
                  <span className="info-label">Created</span>
                  <span className="info-value">{formatDate(selectedReport.createdAt)}</span>
                </div>
                <div className="info-group">
                  <span className="info-label">Size</span>
                  <span className="info-value">{formatFileSize(selectedReport.fileSize)}</span>
                </div>
              </div>

              <div className="detail-actions">
                <button className="btn-download" onClick={() => handleDownload(selectedReport)}>
                  <span className="btn-icon">⬇</span>
                  Download Report
                </button>
                <button
                  className="btn-delete-detail"
                  onClick={() => handleDelete(selectedReport.id)}
                >
                  <span className="btn-icon">🗑️</span>
                  Delete
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ReportViewer;
