export interface Education {
  degree: string;
  institute: string;
  year: string;
  gradeGpa: string;
  marksObtained: number;
  totalMarks: number;
}

export interface Experience {
  orgName: string;
  from: string;
  to: string;
  designation: string;
  grossSalary: number;
  remarks: string;
}

export interface Increment {
  effectiveDate: string;
  newGross: number;
  newHouseRent?: number;
  newUtilityAllowance?: number;
  newOtherAllowance?: number;
  type: 'Hiring' | 'Increment' | 'Promotion' | 'Adjustment' | 'Correction';
  remarks: string;
  createdAt: string;
  createdBy: string;
}

export interface DisciplinaryAction {
  id: string;
  date: string;
  description: string;
  outcome: string;
}

export interface FamilyMember {
  name: string;
  relationship: 'Spouse' | 'Child' | 'Parent' | 'Brother' | 'Sister' | 'Other';
  dob: string;
}

export interface Employee {
  id: string;
  employeeCode: string;
  name: string;
  designation_id?: string;
  grade_id?: string;
  department_id?: string;
  sub_department_id?: string;
  plant_id?: string;
  organization_id?: string;
  shift_id?: string;
  division?: 'White' | 'Black' | 'Nil';
  present_district_id?: string;
  permanent_district_id?: string;
  line_manager_id?: string;

  // Legacy/Display fields (kept for compatibility)
  designation: string;
  grade: string;
  department: string;
  subDepartment?: string;
  hrPlant: string;
  orgName: string;
  shift: string;
  restDay: string;

  // Personal
  maritalStatus: 'Single' | 'Married' | 'Divorced';
  weddingAnniversaryDate?: string;
  bloodGroup: string;
  religion: string;
  nationality: string;
  passportNumber?: string;
  drivingLicense?: string;
  cnic: string;
  cnicIssueDate?: string;
  cnicExpiryDate: string;
  dateOfBirth: string;
  gender?: string;
  fatherName: string;
  motherName?: string;

  // Contact
  reference?: string;
  personalCellNumber: string;
  officialCellNumber?: string;
  phoneNumber?: string;
  personalEmail?: string;
  officialEmail?: string;
  email?: string; // Legacy
  presentAddress: string;
  permanentAddress: string;
  presentDistrict: string;
  permanentDistrict: string;
  millsResidenceBlock?: string;
  millsRoom?: string;

  // Employment
  employmentLevel: string;
  status: 'Active' | 'On Leave' | 'Resigned' | 'Terminated' | 'Retired';
  joiningDate: string;
  confirmationDate?: string;
  probationPeriod?: string;

  leavingDate?: string;
  leavingType?: 'Resignation' | 'SOS' | 'Termination' | 'Retirement' | 'Death' | 'Dismissal';

  // Benefits / Financials
  grossSalary: number;
  paymentMode: 'Cash Payment' | 'Cheque' | 'Bank Transfer';
  bankId?: string; // For bank transfer
  bankAccount?: string;

  // Allowances
  houseRent?: number;
  utilityAllowance?: number;
  otherAllowance?: number;

  // Benefits
  socialSecurityStatus: boolean;
  socialSecurityNumber?: string;
  medicalStatus: boolean;
  eobiStatus: boolean;
  eobiNumber?: string;

  avatar?: string;
  profile_picture?: string;

  // Computed / System
  burnoutRisk?: 'Low' | 'Medium' | 'High' | 'Critical';
  performanceScore?: number;
  sentimentScore?: number;

  // Other
  education: Education[];
  experience: Experience[];
  increments: Increment[];
  discipline: DisciplinaryAction[];
  family: FamilyMember[];
}

export interface OnboardingStep {
  id: string;
  label: string;
  done: boolean;
}

export interface OnboardingNode {
  id: string;
  name: string;
  position: string;
  progress: number;
  startDate: string;
  steps: { label: string; done: boolean }[];
}

export interface NewHireNode {
  id: string;
  name: string;
  role: string;
  progress: number;
  mentor: string;
  startDate: string;
  steps: OnboardingStep[];
}

export interface OffboardingStep {
  id: string;
  label: string;
  done: boolean;
}

export interface ExitNode {
  id: string;
  name: string;
  role: string;
  type: string;
  lDate: string;
  status:
    | 'Initiated'
    | 'Equip. Return'
    | 'Clearance'
    | 'Final Settlement'
    | 'Exit Interview'
    | 'Archived'
    | 'Cleared'
    | 'In Progress';
  checklist: OffboardingStep[];
}

export interface OffboardingExit {
  id: string;
  name: string;
  role: string;
  type: string;
  lDate: string;
  status: string;
  checklist: OffboardingStep[];
}
