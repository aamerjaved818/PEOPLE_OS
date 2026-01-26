/**
 * Analytics Dashboard Components
 * Main component for displaying workforce analytics
 */

import React, { useState, useEffect } from 'react';
import useSWR from 'swr';
import { analyticsApi } from '@/services/analyticsApi';
import MetricCard from './MetricCard';
import TrendChart from './TrendChart';
import RecruitmentFunnel from './RecruitmentFunnel';
import ReportDownloader from './ReportDownloader';
import ReportBuilder from './ReportBuilder';
import ReportViewer from './ReportViewer';
import './AnalyticsDashboard.css';

interface DashboardState {
  loading: boolean;
  error: string | null;
  selectedPeriod: 'current' | '30days' | '90days' | '1year';
}

const AnalyticsDashboard: React.FC = () => {
  const [state, setState] = useState<DashboardState>({
    loading: true,
    error: null,
    selectedPeriod: 'current',
  });

  // Fetch dashboard summary
  const {
    data: dashboard,
    error: dashboardError,
    isLoading: dashboardLoading,
  } = useSWR(
    'dashboard-summary',
    () => analyticsApi.getDashboardSummary().then((res: any) => res.data),
    { revalidateOnFocus: false, dedupingInterval: 60000 } // 1 minute cache
  );

  // Fetch headcount trends
  const { data: trends, error: trendsError } = useSWR(
    'headcount-trends',
    () => analyticsApi.getHeadcountTrends().then((res: any) => res.data),
    { revalidateOnFocus: false, dedupingInterval: 60000 }
  );

  // Fetch recruitment funnel
  const { data: funnel, error: funnelError } = useSWR(
    'recruitment-funnel',
    () => analyticsApi.getRecruitmentFunnel().then((res: any) => res.data),
    { revalidateOnFocus: false, dedupingInterval: 60000 }
  );

  useEffect(() => {
    const hasError = dashboardError || trendsError || funnelError;
    setState((prev) => ({
      ...prev,
      loading: dashboardLoading,
      error: hasError ? 'Failed to load analytics data' : null,
    }));
  }, [dashboardLoading, dashboardError, trendsError, funnelError]);

  if (state.error) {
    return (
      <div className="dashboard-error">
        <div className="error-card">
          <h2>Unable to Load Analytics</h2>
          <p>{state.error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1>Workforce Analytics Dashboard</h1>
        <div className="header-actions">
          <select
            value={state.selectedPeriod}
            onChange={(e) =>
              setState((prev) => ({ ...prev, selectedPeriod: e.target.value as any }))
            }
            className="period-selector"
          >
            <option value="current">Current Period</option>
            <option value="30days">Last 30 Days</option>
            <option value="90days">Last 90 Days</option>
            <option value="1year">Last 12 Months</option>
          </select>
          <ReportDownloader />
        </div>
      </div>

      {/* Loading State */}
      {state.loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading analytics...</p>
        </div>
      )}

      {/* Executive Summary Cards */}
      {dashboard && !state.loading && (
        <>
          <section className="dashboard-section">
            <h2>Executive Summary</h2>
            <div className="metrics-grid">
              <MetricCard
                title="Active Employees"
                value={dashboard.total_active_employees}
                format="number"
                icon="👥"
                trend={dashboard.workforce_velocity}
                trendLabel="Month-over-month"
              />
              <MetricCard
                title="Retention Rate"
                value={dashboard.retention_vector}
                format="percentage"
                icon="📈"
                trend={dashboard.retention_vector}
                trendLabel="Overall retention"
              />
              <MetricCard
                title="Turnover Rate"
                value={dashboard.turnover_rate}
                format="percentage"
                icon="📉"
                trend={dashboard.turnover_rate}
                trendLabel="Annualized"
              />
              <MetricCard
                title="Total Candidates"
                value={dashboard.total_candidates}
                format="number"
                icon="🎯"
                trend={`${dashboard.open_positions} open positions`}
                trendLabel="Pipeline status"
              />
              <MetricCard
                title="Cost per Employee"
                value={dashboard.cost_per_employee}
                format="currency"
                icon="💰"
                trend={`${dashboard.new_hires_30d} new hires`}
                trendLabel="Last 30 days"
              />
              <MetricCard
                title="Monthly Payroll"
                value={`$${(dashboard.total_monthly_payroll / 1000000).toFixed(1)}M`}
                format="text"
                icon="💵"
                trend="Current period"
                trendLabel="Total cost"
              />
            </div>
          </section>

          {/* Department Distribution */}
          <section className="dashboard-section">
            <h2>Department Distribution</h2>
            <div className="distribution-container">
              <div className="distribution-list">
                {dashboard.department_distribution?.map((dept: any, idx: number) => (
                  <div key={idx} className="distribution-item">
                    <span className="dept-name">{dept.name}</span>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${(dept.value / dashboard.total_active_employees) * 100}%`,
                        }}
                      ></div>
                    </div>
                    <span className="dept-count">{dept.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Gender Distribution */}
          <section className="dashboard-section">
            <h2>Gender Distribution</h2>
            <div className="gender-distribution">
              {dashboard.gender_distribution?.map((gender: any, idx: number) => (
                <div key={idx} className="gender-card">
                  <div className="gender-icon">
                    {gender.name === 'Male' ? '👨' : gender.name === 'Female' ? '👩' : '👤'}
                  </div>
                  <h3>{gender.name}</h3>
                  <p className="gender-count">{gender.value}</p>
                  <p className="gender-percentage">
                    {((gender.value / dashboard.total_active_employees) * 100).toFixed(1)}%
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* Headcount Trends */}
          {trends && (
            <section className="dashboard-section">
              <h2>Headcount Trends (6 Months)</h2>
              <TrendChart data={trends} />
            </section>
          )}

          {/* Recruitment Funnel */}
          {funnel && (
            <section className="dashboard-section">
              <h2>Recruitment Pipeline</h2>
              <RecruitmentFunnel stages={funnel} />
            </section>
          )}

          {/* Report Downloads */}
          <section className="dashboard-section">
            <h2>Generate Reports</h2>
            <div className="reports-grid">
              <ReportDownloader reportType="workforce" period={state.selectedPeriod} />
              <ReportDownloader reportType="recruitment" period={state.selectedPeriod} />
              <ReportDownloader reportType="payroll" period={state.selectedPeriod} />
            </div>
          </section>

          {/* Report Builder */}
          <section className="dashboard-section">
            <h2>Custom Reports</h2>
            <ReportBuilder />
          </section>

          {/* Report History */}
          <section className="dashboard-section">
            <h2>Report History</h2>
            <ReportViewer />
          </section>

          {/* Engagement Metrics */}
          <section className="dashboard-section">
            <h2>Engagement Metrics</h2>
            <div className="engagement-placeholder">
              <p>📊 Engagement tracking coming soon</p>
              <p className="small">Requires engagement module integration</p>
            </div>
          </section>
        </>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
