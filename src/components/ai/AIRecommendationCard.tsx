import React from 'react';
import { BrainCircuit, ChevronRight } from 'lucide-react';
import { Button } from '../ui/Button';

interface AIRecommendationCardProps {
  title: string;
  value: string;
}

export const AIRecommendationCard: React.FC<AIRecommendationCardProps> = ({ title, value }) => {
  return (
    <div className="glass-card p-6 flex flex-col justify-between group hover-float bg-gradient-to-br from-primary/5 to-transparent">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-sm font-black text-primary uppercase tracking-wider flex items-center gap-2">
          <BrainCircuit size={16} />
          {title}
        </h3>
      </div>

      <div className="space-y-4">
        <div className="text-lg font-bold text-text-primary leading-tight">"{value}"</div>
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-between group/btn text-[0.65rem] uppercase tracking-widest"
        >
          View Details
          <ChevronRight size={14} className="group-hover/btn:translate-x-1 transition-transform" />
        </Button>
      </div>
    </div>
  );
};
