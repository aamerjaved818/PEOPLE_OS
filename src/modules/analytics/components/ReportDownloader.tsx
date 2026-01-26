/**
 * ReportDownloader Component
 * Handles report generation and download with format selection
 */

import React, { useState } from 'react';
import { API_CONFIG } from '@/config/constants';
import './ReportDownloader.css';

interface ReportDownloaderProps {
  reportType?: 'workforce' | 'recruitment' | 'payroll' | 'all';
  period?: 'current' | '30days' | '90days' | '1year';
  isLoading?: boolean;
}

type ReportFormat = 'pdf' | 'excel';

const ReportDownloader: React.FC<ReportDownloaderProps> = ({
  reportType = 'workforce',
  period = 'current',
  isLoading = false,
}) => {
  const [selectedFormat, setSelectedFormat] = useState<ReportFormat>('pdf');
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async (format: ReportFormat) => {
    setDownloading(true);
    setError(null);

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/analytics/download-report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
        body: JSON.stringify({
          report_type: reportType,
          format: format,
          period: period,
        }),
      });

      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }

      const blob = await response.blob();
      const contentDisposition = response.headers.get('content-disposition');
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : `${reportType}_report.${format === 'pdf' ? 'pdf' : 'xlsx'}`;

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed');
      console.error('Report download error:', err);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="report-downloader">
      <div className="downloader-header">
        <h3>Generate Report</h3>
        <p className="downloader-subtitle">Export analytics as PDF or Excel</p>
      </div>

      <div className="format-selector">
        <label className="format-option">
          <input
            type="radio"
            name="format"
            value="pdf"
            checked={selectedFormat === 'pdf'}
            onChange={(e) => setSelectedFormat(e.target.value as ReportFormat)}
            disabled={downloading || isLoading}
          />
          <span className="option-content">
            <span className="option-icon">📄</span>
            <span className="option-text">
              <span className="option-title">PDF Report</span>
              <span className="option-description">Professional formatted document</span>
            </span>
          </span>
        </label>

        <label className="format-option">
          <input
            type="radio"
            name="format"
            value="excel"
            checked={selectedFormat === 'excel'}
            onChange={(e) => setSelectedFormat(e.target.value as ReportFormat)}
            disabled={downloading || isLoading}
          />
          <span className="option-content">
            <span className="option-icon">📊</span>
            <span className="option-text">
              <span className="option-title">Excel Workbook</span>
              <span className="option-description">Multi-sheet spreadsheet data</span>
            </span>
          </span>
        </label>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="downloader-actions">
        <button
          className="download-button"
          onClick={() => handleDownload(selectedFormat)}
          disabled={downloading || isLoading}
        >
          {downloading ? (
            <>
              <span className="spinner">⟳</span>
              Downloading...
            </>
          ) : (
            <>
              <span className="button-icon">⬇</span>
              Download {selectedFormat.toUpperCase()}
            </>
          )}
        </button>
      </div>

      <div className="downloader-footer">
        <p className="report-info">
          <span className="info-item">
            <span className="info-label">Report Type:</span>
            <span className="info-value">{reportType}</span>
          </span>
          <span className="info-item">
            <span className="info-label">Period:</span>
            <span className="info-value">{period}</span>
          </span>
        </p>
      </div>
    </div>
  );
};

export default ReportDownloader;
