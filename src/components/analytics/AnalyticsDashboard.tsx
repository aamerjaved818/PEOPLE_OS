import React, { useState } from 'react';
import { BarChart3, Clock, AlertCircle } from 'lucide-react';
import ScheduleManager from './ScheduleManager';
import TaskMonitor from './TaskMonitor';
import TrendChart from './TrendChart';
import RecruitmentFunnel from './RecruitmentFunnel';
import ReportDownloader from './ReportDownloader';
import ReportBuilder from './ReportBuilder';

type TabType = 'overview' | 'schedules' | 'tasks' | 'reports' | 'builder';

interface DashboardTab {
  id: TabType;
  label: string;
  icon: React.ReactNode;
  description: string;
}

const AnalyticsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const tabs: DashboardTab[] = [
    {
      id: 'overview',
      label: 'Overview',
      icon: <BarChart3 size={20} />,
      description: 'Key metrics and trends',
    },
    {
      id: 'schedules',
      label: 'Schedules',
      icon: <Clock size={20} />,
      description: 'Manage recurring reports',
    },
    {
      id: 'tasks',
      label: 'Tasks',
      icon: <AlertCircle size={20} />,
      description: 'Monitor report generation',
    },
    {
      id: 'reports',
      label: 'Reports',
      icon: <BarChart3 size={20} />,
      description: 'Download and manage reports',
    },
    {
      id: 'builder',
      label: 'Builder',
      icon: <BarChart3 size={20} />,
      description: 'Create custom reports',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">
            View metrics, manage schedules, and build custom reports
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`p-4 rounded-lg border transition ${
                activeTab === tab.id
                  ? 'bg-blue-50 border-blue-300 text-blue-900'
                  : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
              }`}
            >
              <div className="flex flex-col items-center gap-2">
                {tab.icon}
                <span className="text-sm font-medium">{tab.label}</span>
                <span className="text-xs text-gray-500">{tab.description}</span>
              </div>
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Trends</h2>
                <TrendChart />
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Recruitment Pipeline</h2>
                <RecruitmentFunnel />
              </div>
            </div>
          )}

          {activeTab === 'schedules' && (
            <div className="bg-white rounded-lg shadow">
              <ScheduleManager onScheduleCreated={() => {}} />
            </div>
          )}

          {activeTab === 'tasks' && (
            <div className="bg-white rounded-lg shadow">
              <TaskMonitor refreshInterval={5000} maxTasks={10} />
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Generated Reports</h2>
              <ReportDownloader />
            </div>
          )}

          {activeTab === 'builder' && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Custom Report Builder</h2>
              <ReportBuilder />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
