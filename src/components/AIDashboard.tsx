import React from 'react';
import { useAI } from '@/hooks/useAI';
import { AIInsightCard } from './ai/AIInsightCard';
import { AIPredictionCard } from './ai/AIPredictionCard';
import { AIRecommendationCard } from './ai/AIRecommendationCard';
import ModuleSkeleton from './ui/ModuleSkeleton';

export const AIDashboard: React.FC = () => {
  const { insights, predictions, recommendations, loading } = useAI();

  if (loading) {
    return <ModuleSkeleton />;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <AIInsightCard
        title="Employee Sentiment"
        value={insights.sentiment}
        trend={insights.sentimentTrend}
      />
      <AIPredictionCard
        title="Turnover Risk"
        value={predictions.turnoverRisk}
        action={recommendations.retentionAction}
      />
      <AIRecommendationCard title="Hiring Forecast" value={recommendations.hiringForecast} />
    </div>
  );
};

export default AIDashboard;
