import React, { useState } from 'react';
import { Download, FileText, Calendar } from 'lucide-react';

interface Report {
  id: string;
  name: string;
  type: string;
  format: string;
  size: string;
  generated_at: string;
}

const mockReports: Report[] = [
  {
    id: '1',
    name: 'Monthly Sales Report',
    type: 'Sales',
    format: 'PDF',
    size: '2.4 MB',
    generated_at: '2024-01-15',
  },
  {
    id: '2',
    name: 'Q4 Recruitment Summary',
    type: 'Recruitment',
    format: 'Excel',
    size: '1.8 MB',
    generated_at: '2024-01-10',
  },
  {
    id: '3',
    name: 'Performance Review Dashboard',
    type: 'Performance',
    format: 'PDF',
    size: '3.2 MB',
    generated_at: '2024-01-05',
  },
];

interface ReportDownloaderProps {
  onDownload?: (reportId: string) => void;
}

const ReportDownloader: React.FC<ReportDownloaderProps> = ({ onDownload }) => {
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleDownload = async (report: Report) => {
    setDownloading(report.id);
    try {
      // Simulate download
      await new Promise((resolve) => setTimeout(resolve, 1000));
      onDownload?.(report.id);
      // In real implementation, trigger actual download
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="space-y-4">
      {mockReports.map((report) => (
        <div
          key={report.id}
          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
        >
          <div className="flex items-center gap-4 flex-1 min-w-0">
            <FileText className="text-blue-600 flex-shrink-0" size={24} />
            <div className="min-w-0 flex-1">
              <h3 className="font-medium text-gray-900 truncate">{report.name}</h3>
              <div className="flex gap-4 text-sm text-gray-600 mt-1">
                <span>{report.type}</span>
                <span>•</span>
                <span>{report.format}</span>
                <span>•</span>
                <span>{report.size}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4 ml-4 flex-shrink-0">
            <div className="flex items-center gap-1 text-sm text-gray-600">
              <Calendar size={16} />
              {report.generated_at}
            </div>
            <button
              onClick={() => handleDownload(report)}
              disabled={downloading === report.id}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 flex items-center gap-2"
            >
              <Download size={18} />
              {downloading === report.id ? 'Downloading...' : 'Download'}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ReportDownloader;
