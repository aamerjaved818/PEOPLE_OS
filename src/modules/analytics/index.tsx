import React, { useState, useEffect } from 'react';
import {
  Download,
  Filter,
  RefreshCw,
  Activity,
  Target,
  BrainCircuit,
  Database,
  FileText,
  Table as TableIcon,
} from 'lucide-react';
import { COLORS } from './constants';
import {
  analyticsApi,
  DashboardSummary,
  TrendDataPoint,
  EngagementDataPoint,
  AnalyticsDataPoint,
} from '@/services/analyticsApi';

// Sub-components
import AnalyticsStats from './AnalyticsStats';
import ProductivityMatrix from './ProductivityMatrix';
import NeuralModeling from './NeuralModeling';
import ClusterDensity from './ClusterDensity';
import EntropyAlert from './EntropyAlert';
import EfficiencyPulse from './EfficiencyPulse';
import ForecastingMatrix from './ForecastingMatrix';
import PredictiveWorkforce from './PredictiveWorkforce';
import RecruitmentFunnel from './RecruitmentFunnel';
import Modal from '@/components/ui/Modal';

const AnalyticsInsights: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trends, setTrends] = useState<TrendDataPoint[]>([]);
  const [engagement, setEngagement] = useState<EngagementDataPoint[]>([]);
  const [recruitment, setRecruitment] = useState<AnalyticsDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [showExportModal, setShowExportModal] = useState(false);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const [summaryRes, trendsRes, engagementRes, recruitmentRes] = await Promise.all([
        analyticsApi.getDashboardSummary(),
        analyticsApi.getHeadcountTrends(),
        analyticsApi.getEngagementData(),
        analyticsApi.getRecruitmentFunnel(),
      ]);
      setSummary(summaryRes.data);
      setTrends(trendsRes.data);
      setEngagement(engagementRes.data);
      setRecruitment(recruitmentRes.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-[60vh] flex flex-col items-center justify-center space-y-4">
        <RefreshCw className="w-12 h-12 text-primary animate-spin" />
        <p className="text-muted-foreground font-black uppercase tracking-widest text-xs">
          Synchronizing Neural Interface...
        </p>
      </div>
    );
  }

  const stats = summary
    ? [
        {
          label: 'Workforce Velocity',
          val: summary.workforce_velocity,
          trend: '+4.5',
          icon: Activity,
          color: 'blue',
        },
        {
          label: 'Retention Vector',
          val: summary.retention_vector,
          trend: '+2.1',
          icon: Target,
          color: 'indigo',
        },
        {
          label: 'Neural Alignment',
          val: summary.neural_alignment,
          trend: '+0.5',
          icon: BrainCircuit,
          color: 'emerald',
        },
        {
          label: 'Asset Equity',
          val: summary.asset_equity,
          trend: 'Optimal',
          icon: Database,
          color: 'orange',
        },
      ]
    : [];

  const handleExport = (format: 'pdf' | 'excel') => {
    analyticsApi.downloadReport(format, 'workforce');
    setShowExportModal(false);
  };

  return (
    <div className="space-y-12 animate-in fade-in duration-700 pb-20">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
        <div>
          <h1 className="text-4xl font-black text-foreground tracking-tighter leading-none uppercase antialiased">
            Analytics
          </h1>
          <p className="text-muted-foreground mt-4 font-black uppercase tracking-[0.4em] text-[0.75rem] flex items-center gap-4">
            <span className="w-10 h-[0.125rem] bg-primary"></span>
            Workforce Intelligence & Strategic Projection
          </p>
        </div>
        <div className="flex gap-4 p-4 bg-card rounded-[2rem] shadow-2xl border border-border">
          <button
            aria-label="Filter analytics"
            className="bg-secondary p-4 rounded-2xl text-muted-foreground hover:text-primary transition-all"
          >
            <Filter size={20} />
          </button>
          <button
            onClick={() => setShowExportModal(true)}
            className="bg-primary text-primary-foreground px-12 py-4 rounded-[1.375rem] font-black uppercase text-[0.625rem] tracking-widest flex items-center gap-4 shadow-2xl hover:scale-105 active:scale-95 transition-all"
          >
            <Download size={18} /> Export Report
          </button>
        </div>
      </div>

      <AnalyticsStats stats={stats} />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
        <div className="lg:col-span-8 space-y-12">
          <ProductivityMatrix data={engagement} />
          <RecruitmentFunnel data={recruitment} />
          <ForecastingMatrix data={trends} />
          <PredictiveWorkforce />
          <NeuralModeling />
        </div>

        <div className="lg:col-span-4 space-y-12">
          <ClusterDensity data={summary?.department_distribution || []} colors={COLORS} />
          <EntropyAlert />
          <EfficiencyPulse />
        </div>
      </div>

      {/* Export Modal */}
      <Modal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        title="Export Intelligence Report"
        size="sm"
      >
        <div className="space-y-6">
          <p className="text-sm text-text-muted">
            Select the output format for your comprehensive workforce intelligence report.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => handleExport('pdf')}
              className="group p-6 bg-muted-bg/30 border border-border rounded-2xl hover:border-primary hover:bg-primary/5 transition-all text-center"
            >
              <div className="w-12 h-12 bg-rose-500/10 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <FileText className="text-rose-600" size={24} />
              </div>
              <span className="text-xs font-black uppercase tracking-widest text-text-primary">
                PDF Document
              </span>
            </button>
            <button
              onClick={() => handleExport('excel')}
              className="group p-6 bg-muted-bg/30 border border-border rounded-2xl hover:border-emerald-500 hover:bg-emerald-500/5 transition-all text-center"
            >
              <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <TableIcon className="text-emerald-600" size={24} />
              </div>
              <span className="text-xs font-black uppercase tracking-widest text-text-primary">
                Excel Dataset
              </span>
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default AnalyticsInsights;
