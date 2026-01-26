/**
 * MetricCard Component
 * Displays individual metric with trend and status
 */

import React from 'react';
import './MetricCard.css';

interface MetricCardProps {
  title: string;
  value: string | number;
  format: 'number' | 'percentage' | 'currency' | 'text';
  icon: string;
  trend?: string;
  trendLabel?: string;
  onClick?: () => void;
  isLoading?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  format,
  icon,
  trend,
  trendLabel,
  onClick,
  isLoading = false,
}) => {
  const formatValue = (val: string | number): string => {
    if (typeof val === 'string') {
      return val;
    }

    switch (format) {
      case 'percentage':
        return `${val}%`;
      case 'currency':
        return typeof val === 'string' ? val : `$${val.toLocaleString()}`;
      case 'number':
        return val.toLocaleString();
      case 'text':
      default:
        return String(val);
    }
  };

  const getTrendColor = (trend: string | undefined): 'positive' | 'negative' | 'neutral' => {
    if (!trend) {
      return 'neutral';
    }

    const numTrend = parseFloat(trend);
    if (isNaN(numTrend)) {
      return 'neutral';
    }

    if (title.includes('Retention') || title.includes('Employees')) {
      return numTrend >= 0 ? 'positive' : 'negative';
    }

    if (title.includes('Turnover')) {
      return numTrend <= 0 ? 'positive' : 'negative';
    }

    return numTrend >= 0 ? 'positive' : 'negative';
  };

  return (
    <div
      className={`metric-card ${isLoading ? 'loading' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : -1}
    >
      <div className="metric-header">
        <span className="metric-icon">{icon}</span>
        <h3 className="metric-title">{title}</h3>
      </div>

      {isLoading ? (
        <div className="metric-skeleton">
          <div className="skeleton-value"></div>
        </div>
      ) : (
        <>
          <div className="metric-value">
            <span className="value">{formatValue(value)}</span>
          </div>

          {trend && (
            <div className={`metric-trend ${getTrendColor(trend)}`}>
              <span className="trend-icon">
                {getTrendColor(trend) === 'positive' ? '📈' : '📉'}
              </span>
              <span className="trend-value">{trend}</span>
              {trendLabel && <span className="trend-label">{trendLabel}</span>}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default MetricCard;
