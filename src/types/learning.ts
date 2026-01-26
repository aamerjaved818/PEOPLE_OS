import { LucideIcon } from 'lucide-react';

export interface Course {
  id: number;
  title: string;
  provider: string;
  duration: string;
  level: string;
  score: number;
  status: 'Completed' | 'In Progress' | 'Enrolled' | 'Recommended';
  progress?: number;
  icon?: LucideIcon | string; // Keeping as any for now as it stores Lucide icon components in mock data, but in real app this might be a string identifier
  color: string;
}
