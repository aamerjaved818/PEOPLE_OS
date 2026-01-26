export interface Goal {
  id: string; // Changed from number
  title: string;
  category: 'Operational' | 'Strategic' | 'Culture' | 'Development';
  progress: number;
  metric: string; // Added
  status: string;
  dueDate: string; // Added
  weight: number;
  description: string; // Added
  trend?: 'up' | 'down' | 'neutral'; // Optional now as backend doesn't have it yet? Or computed?
}
