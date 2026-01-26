export type ConfigValue =
  | string
  | number
  | boolean
  | null
  | undefined
  | Record<string, unknown>
  | unknown[];

export type ModuleType =
  | 'dashboard'
  | 'employees'
  | 'org-settings'
  | 'recruitment'
  | 'job-postings'
  | 'onboarding'
  | 'offboarding'
  | 'attendance'
  | 'leaves'
  | 'overtime'
  | 'payroll'
  | 'tax-compliance'
  | 'compensation'
  | 'benefits'
  | 'performance'
  | 'promotions'
  | 'learning'
  | 'skills'
  | 'succession'
  | 'engagement'
  | 'rewards'
  | 'relations'
  | 'health-safety'
  | 'travel'
  | 'expenses'
  | 'assets'
  | 'alumni'
  | 'analytics'
  | 'workflow'
  | 'neural'
  | 'system-settings'
  | 'integration'
  | 'self-service'
  | 'admin'
  | 'visitors'
  | 'assistance'
  | 'system-health'
  | 'hcm'
  | 'people-os-chat'
  | 'system-audit'
  | 'org-audit'
  | 'promotions';

// Common interfaces if any
