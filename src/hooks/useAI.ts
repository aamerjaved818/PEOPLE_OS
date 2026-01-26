import { useState, useEffect } from 'react';

// Mock data for AI service
const MOCK_AI_DATA = {
  insights: {
    sentiment: 78, // 0-100 score
    sentimentTrend: '+4.2%',
  },
  predictions: {
    turnoverRisk: 'Low',
    riskScore: 12,
  },
  recommendations: {
    retentionAction: 'Schedule 1:1 with Team Lead',
    hiringForecast: 'Need 3 Engineers in Q3',
    suggestedTraining: 'Advanced React Patterns',
  },
};

interface AIState {
  insights: {
    sentiment: number;
    sentimentTrend: string;
  };
  predictions: {
    turnoverRisk: string;
    riskScore: number;
  };
  recommendations: {
    retentionAction: string;
    hiringForecast: string;
    suggestedTraining: string;
  };
  loading: boolean;
  error: string | null;
}

export function useAI() {
  const [data, setData] = useState<AIState>({
    insights: { sentiment: 0, sentimentTrend: '0%' },
    predictions: { turnoverRisk: 'Unknown', riskScore: 0 },
    recommendations: { retentionAction: '', hiringForecast: '', suggestedTraining: '' },
    loading: true,
    error: null,
  });

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setData({
        ...MOCK_AI_DATA,
        loading: false,
        error: null,
      });
    }, 1200);

    return () => clearTimeout(timer);
  }, []);

  return data;
}
