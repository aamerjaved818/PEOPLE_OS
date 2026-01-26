import { Employee } from './hcm';
import { Designation, Grade } from './org';

export interface PromotionCycle {
  id: number;
  title: string;
  status: 'Open' | 'Processing' | 'Completed';
  startDate?: string;
  endDate?: string;
  organizationId: string;
  createdAt: string;
}

export interface PromotionApproval {
  id: number;
  requestId: number;
  approverId: string;
  level: 'HR' | 'Finance' | 'Final';
  status: 'Approved' | 'Rejected';
  remarks?: string;
  createdAt: string;
}

export interface PromotionRequest {
  id: number;
  cycleId?: number;
  employeeId: string;
  type: 'Increment' | 'Promotion' | 'Both';
  currentSalary: number;
  proposedSalary: number;
  currentDesignationId?: string;
  proposedDesignationId?: string;
  currentGradeId?: string;
  proposedGradeId?: string;
  reason?: string;
  performanceRating?: string;
  managerRemarks?: string;
  status:
    | 'Pending'
    | 'HR_Approved'
    | 'Finance_Approved'
    | 'Final_Approved'
    | 'Implemented'
    | 'Rejected';
  effectiveDate: string;
  organizationId: string;
  approvals: PromotionApproval[];
  employee?: Employee;
  currentDesignation?: Designation;
  proposedDesignation?: Designation;
  currentGrade?: Grade;
  proposedGrade?: Grade;
  createdAt: string;
}
