/**
 * Analytics API Integration
 * Handles all workforce intelligence and reporting API calls
 */

import { api } from '../services/api';
import { API_CONFIG } from '../config/constants';

// ===== Types =====

export interface AnalyticsDataPoint {
  name: string;
  value: number;
}

export interface TrendDataPoint {
  name: string;
  count: number;
  liability: number;
}

export interface EngagementDataPoint {
  name: string;
  engagement: number;
  productivity: number;
  sentiment: number;
}

export interface DashboardSummary {
  workforce_velocity: string;
  retention_vector: string;
  neural_alignment: string;
  asset_equity: string;
  total_active_employees: number;
  total_candidates: number;
  department_distribution: AnalyticsDataPoint[];
  gender_distribution: AnalyticsDataPoint[];
}

// ===== API Client =====

export const analyticsApi = {
  /**
   * Get high-level workforce analytics summary
   */
  getDashboardSummary: async (): Promise<{ data: DashboardSummary }> => {
    const data = await api.get('/analytics/dashboard');
    return { data };
  },

  /**
   * Get monthly headcount and liability trends
   */
  getHeadcountTrends: async (): Promise<{ data: TrendDataPoint[] }> => {
    const data = await api.get('/analytics/trends/headcount');
    return { data };
  },

  /**
   * Get candidate distribution by recruitment stage
   */
  getRecruitmentFunnel: async (): Promise<{ data: AnalyticsDataPoint[] }> => {
    const data = await api.get('/analytics/recruitment/funnel');
    return { data };
  },

  /**
   * Get weekly engagement, productivity and sentiment metrics
   */
  getEngagementData: async (): Promise<{ data: EngagementDataPoint[] }> => {
    const data = await api.get('/analytics/engagement');
    return { data };
  },

  /**
   * Generate and download reports
   */
  downloadReport: (format: 'pdf' | 'excel', type: 'workforce' | 'payroll' | 'recruitment') => {
    const baseUrl = API_CONFIG.BASE_URL;
    const url = `${baseUrl}/analytics/reports?format=${format}&type=${type}`;
    window.open(url, '_blank');
  },
};
