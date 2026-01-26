/**
 * RecruitmentFunnel Component
 * Displays recruitment pipeline with funnel visualization
 */

import React from 'react';
import './RecruitmentFunnel.css';

interface FunnelStage {
  name: string;
  count: number;
  percentage: number;
}

interface RecruitmentFunnelProps {
  stages: FunnelStage[];
  title?: string;
  isLoading?: boolean;
}

const RecruitmentFunnel: React.FC<RecruitmentFunnelProps> = ({
  stages,
  title = 'Recruitment Funnel',
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <div className="recruitment-funnel">
        <h3 className="funnel-title">{title}</h3>
        <div className="funnel-loading">Loading...</div>
      </div>
    );
  }

  const maxCount = Math.max(...stages.map((s) => s.count), 1);
  const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="recruitment-funnel">
      <h3 className="funnel-title">{title}</h3>

      <div className="funnel-container">
        {stages.map((stage, index) => {
          const width = (stage.count / maxCount) * 100;
          const color = colors[index % colors.length];

          return (
            <div key={stage.name} className="funnel-stage-wrapper">
              <div className="funnel-stage-label">
                <span className="stage-name">{stage.name}</span>
                <span className="stage-count">{stage.count}</span>
              </div>

              <div className="funnel-stage-container">
                <div
                  className="funnel-stage"
                  style={{
                    width: `${width}%`,
                    backgroundColor: color,
                    minWidth: '20px',
                  }}
                >
                  <span className="stage-percentage">{stage.percentage}%</span>
                </div>
              </div>

              {index < stages.length - 1 && (
                <div className="funnel-drop">
                  <span className="drop-value">
                    ↓{' '}
                    {(
                      ((stages[index].count - stages[index + 1].count) / stages[index].count) *
                      100
                    ).toFixed(1)}
                    % drop
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="funnel-summary">
        <div className="summary-metric">
          <span className="metric-label">Total Candidates</span>
          <span className="metric-value">{stages[0]?.count || 0}</span>
        </div>
        <div className="summary-metric">
          <span className="metric-label">Conversion Rate</span>
          <span className="metric-value">
            {stages.length > 1
              ? ((stages[stages.length - 1]?.count / stages[0]?.count) * 100).toFixed(1)
              : 0}
            %
          </span>
        </div>
        <div className="summary-metric">
          <span className="metric-label">Offers Extended</span>
          <span className="metric-value">{stages[stages.length - 1]?.count || 0}</span>
        </div>
      </div>
    </div>
  );
};

export default RecruitmentFunnel;
