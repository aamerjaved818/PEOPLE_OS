export interface GrowthTrend {
  name: string;
  headcount: number;
  turnover: number;
}

export interface Milestone {
  id: number;
  name: string;
  type: 'Birthday' | 'Anniversary' | 'Wedding';
  date: string;
  avatar: string;
  detail: string;
}

export interface DepartmentStat {
  name: string;
  value: number;
}
