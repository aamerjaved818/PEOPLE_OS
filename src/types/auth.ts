export type UserType = 'SystemAdmin' | 'OrgUser';

export type SystemRole =
  | 'Root'
  | 'Super Admin'
  | 'SystemAdmin'
  | 'Business Admin'
  | 'Manager'
  | 'User';

export type Permission =
  | '*'
  | 'view_dashboard'
  | 'manage_employees'
  | 'view_employees'
  | 'create_employee'
  | 'edit_employee'
  | 'delete_employee'
  | 'manage_payroll'
  | 'view_payroll'
  | 'run_payroll'
  | 'view_salary'
  | 'manage_recruitment'
  | 'view_recruitment'
  | 'view_candidates'
  | 'edit_candidate'
  | 'view_departments'
  | 'view_reports'
  | 'view_audit_logs'
  | 'view_users'
  | 'create_users'
  | 'edit_users'
  | 'delete_users'
  | 'view_profile'
  | 'view_team'
  | 'view_leaves'
  | 'payroll_access'
  | 'manage_master_data'
  | 'system_config'
  | 'employee_management'
  | 'manage_api_keys'
  | 'backup_restore'
  | 'approve_leaves'
  | 'view_own_leaves'
  | 'manage_leaves'
  | 'manage_attendance'
  | 'process_payroll'
  | 'manage_benefits'
  | 'view_financials'
  | 'manage_assets';

export interface User {
  id: string;
  username: string; // Added backend requirement
  password?: string; // Added for creation/update only
  name: string;
  email: string;
  userType: UserType;
  role: SystemRole; // System roles only - Org roles TBD
  status: 'Active' | 'Inactive' | 'Locked';
  profileStatus?: 'Active' | 'Inactive'; // For OrgUser linked profiles
  avatar?: string;
  employeeId?: string; // Link to Employee profile
  organizationId?: string; // Organization association for OrgUsers
  lastLogin?: string;
  department?: string;
  phone?: string;
  isSystemUser?: boolean; // Backend flag for system administrators
}

export interface RoleDefinition {
  id: string;
  organizationId: string;
  name: string;
  description: string;
  permissions: string[]; // JSON or separate relation
  scope: 'Global' | 'Department' | 'Self';
  isSystem: boolean; // Prevent deletion of default roles
}
