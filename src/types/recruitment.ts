export interface JobVacancy {
  id: string;
  title: string;
  department: string;
  location: string;
  type: 'Full-time' | 'Contract' | 'Remote';
  salaryRange: string; // Changed from salary
  status: 'Active' | 'Paused' | 'Closed';
  applicants: number; // Changed from applicantsCount
  description: string;
  postedDate: string;
}

export interface Candidate {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  positionApplied: string;
  currentStage: 'Applied' | 'Screening' | 'Interview' | 'Offer' | 'Hired' | 'Rejected';
  score: number; // AI Fit Score
  resumeUrl: string;
  skills: string[];
  appliedDate: string;
  avatar: string;
}
