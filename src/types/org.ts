import { ConfigValue } from './shared';

export interface OrganizationProfile {
  id: string;
  name: string;
  industry: string;
  logo?: string;
  coverUrl?: string; // New
  currency: string;
  taxYearEnd: string;
  country: string;
  code?: string;
  email?: string;
  website?: string;
  phone?: string;
  status?: 'Active' | 'Inactive';

  description?: string;
  headId?: string; // ID of the Organization Head

  // New Legal & Address Fields
  taxId?: string;
  registrationNumber?: string;
  foundedDate?: string;
  addressLine1?: string;
  addressLine2?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  socialLinks?:
    | string
    | {
        linkedin?: string;
        twitter?: string;
        facebook?: string;
        instagram?: string;
      };

  // Advanced/System Fields
  enabledModules?: string; // JSON array of enabled modules
  systemAuthority?: string; // System-level permissions
  approvalWorkflows?: string; // Workflow configuration JSON

  // Phase 2: System Authority Fields (Settings)
  defaultLanguage?: string;
  timezone?: string;
  dateFormat?: string;
}

export interface OrganizationWithAdmin extends Partial<OrganizationProfile> {
  adminUsername: string;
  adminPassword: string;
  adminName?: string;
  adminEmail?: string;
}

export interface OrganizationAddress {
  id: string;
  organizationId: string;
  type: 'Billing' | 'Shipping' | 'HQ';
  addressLine1: string;
  addressLine2?: string;
  city: string;
  state: string;
  country: string;
  zipCode: string;
  isPrimary: boolean;
}

export interface OrgPolicy {
  id: string;
  organizationId: string;
  type: 'Leave' | 'Attendance' | 'Approval' | 'Payroll' | 'Recruitment';
  name: string;
  description?: string;
  config: Record<string, ConfigValue>; // JSON configuration
  isActive: boolean;
  version: string;
}

export interface PlantDivision {
  id?: string;
  name: string;
  code: string;
  isActive: boolean;
  plantId?: string;
}

export interface Plant {
  id: string;
  name: string;
  code: string;
  location: string;
  headOfPlant?: string;
  contactNumber?: string;
  organizationId?: string;
  divisions?: PlantDivision[];
  isActive: boolean;
  currentSequence?: number;
}

export interface Department {
  id: string;
  name: string;
  subDepartments: string[];
  headOfDept?: string;
  budgetCode?: string;
  code: string;
  parentDepartmentId?: string;
  isActive?: boolean;
  hodId?: string; // Link to Employee (HOD)
  plantId?: string; // Link to Plant
}

export interface SubDepartment {
  id: string;
  name: string;
  code: string;
  parentDepartmentId: string;
  isActive?: boolean;
  organizationId?: string;
}

export interface JobLevel {
  id: string;
  name: string;
  code: string; // e.g. "EL-1", "EL-2"
  description?: string;
  isActive: boolean;
  organizationId: string;
}

export interface Grade {
  id: string;
  name: string;
  level: number; // e.g. 1 (Highest), 10 (Lowest)
  jobLevelId: string; // Link to JobLevel
  isActive: boolean;
  code?: string;
  organizationId: string;
}

export interface Designation {
  id: string;
  name: string;
  gradeId: string;
  departmentId?: string; // Link to Structural Hierarchy
  isActive?: boolean;
}

export interface DesignationGrade {
  grade: string;
  designations: string[];
}

export interface Bank {
  id: string;
  name: string;
  branchCode: string;
  accountNumber: string;
  iban: string;
  swiftCode?: string;
  address?: string;
  contactPerson?: string;
}

export interface Position {
  id: string;
  organizationId: string;
  title: string;
  code: string;
  description?: string;
  departmentId: string; // Link to Department
  designationId?: string; // Link to Master Designation
  reportsToPositionId?: string; // Hierarchy
  jobFamily?: string;
  level?: string;
  isActive: boolean;
}
