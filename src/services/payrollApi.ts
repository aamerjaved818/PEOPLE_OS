/**
 * Payroll API Integration
 * Handles all payroll management API calls
 */

import { api } from '../services/api';
import { API_CONFIG } from '../config/constants';

// ===== Types =====

export interface SalaryComponent {
  id: string;
  code: string;
  name: string;
  description?: string;
  componentType: 'earning' | 'deduction';
  calculationType: 'fixed' | 'percentage';
  percentageOf?: string;
  defaultAmount: number;
  isTaxable: boolean;
  isStatutory: boolean;
  isActive: boolean;
  displayOrder: number;
}

export interface TaxSlab {
  id: string;
  taxYear: string;
  minIncome: number;
  maxIncome?: number;
  fixedTax: number;
  taxRate: number;
  excessOver: number;
  isActive: boolean;
}

export interface TaxDeductionType {
  id: string;
  code: string;
  name: string;
  section: string;
  description?: string;
  deductionType: 'allowance' | 'credit';
  maxIncomeLimit?: number;
  calcPercentage?: number;
  calcIncomePercentage?: number;
  calcPerUnitLimit?: number;
  requiresDocument: boolean;
  requiresNtn: boolean;
}

export interface EmployeeTaxDeduction {
  id: number;
  employeeId: string;
  deductionTypeId: string;
  taxYear: string;
  claimedAmount: number;
  approvedAmount?: number;
  numberOfChildren?: number;
  institutionName?: string;
  institutionNtn?: string;
  status: 'Pending' | 'Approved' | 'Rejected';
  deductionTypeName?: string;
  deductionSection?: string;
}

export interface PayrollRun {
  id: string;
  periodMonth: string;
  periodYear: string;
  status: 'Draft' | 'Processing' | 'Processed' | 'Paid';
  totalEmployees: number;
  processedEmployees: number;
  totalGross: number;
  totalDeductions: number;
  totalNet: number;
  processedAt?: string;
  processedBy?: string;
}

export interface PayslipDetail {
  id: number;
  employeeId: string;
  employeeName?: string;
  employeeCode?: string;
  periodMonth: string;
  periodYear: string;
  basicSalary: number;
  houseRent: number;
  medicalAllowance: number;
  transportAllowance: number;
  otherAllowances: number;
  grossSalary: number;
  incomeTax: number;
  eobiDeduction: number;
  socialSecurity: number;
  loanDeduction: number;
  otherDeductions: number;
  totalDeductions: number;
  netSalary: number;
  status: string;
}

export interface TaxCalculationDetail {
  employeeId: string;
  taxYear: string;
  annualGrossIncome: number;
  section60dTuition: number;
  otherAllowances: number;
  totalDeductibleAllowances: number;
  taxableIncome: number;
  grossTax: number;
  charitableDonationCredit: number;
  insuranceCredit: number;
  totalTaxCredits: number;
  annualTaxPayable: number;
  monthlyTax: number;
}

export interface EmployeeSalaryStructure {
  id: number;
  employeeId: string;
  componentId: string;
  amount: number;
  percentage?: number;
  effectiveFrom: string;
  effectiveTo?: string;
  isActive: boolean;
  componentName?: string;
  componentType?: string;
}

// ===== API Client =====

export const payrollApi = {
  // --- Salary Components ---
  getSalaryComponents: async (activeOnly = true): Promise<{ data: SalaryComponent[] }> => {
    const data = await api.get(`/payroll/components?active_only=${activeOnly}`);
    return { data };
  },

  createSalaryComponent: async (
    componentData: Omit<SalaryComponent, 'id'>
  ): Promise<{ data: SalaryComponent }> => {
    const data = await api.post('/payroll/components', componentData);
    return { data };
  },

  updateSalaryComponent: async (
    id: string,
    componentData: Partial<SalaryComponent>
  ): Promise<{ data: SalaryComponent }> => {
    const data = await api.put(`/payroll/components/${id}`, componentData);
    return { data };
  },

  deleteSalaryComponent: async (id: string): Promise<void> => {
    await api.delete(`/payroll/components/${id}`);
  },

  // --- Tax Slabs ---
  getTaxSlabs: async (taxYear?: string): Promise<{ data: TaxSlab[] }> => {
    const params = taxYear ? `?tax_year=${taxYear}` : '';
    const data = await api.get(`/payroll/tax-slabs${params}`);
    return { data };
  },

  createTaxSlab: async (slabData: Omit<TaxSlab, 'id'>): Promise<{ data: TaxSlab }> => {
    const data = await api.post('/payroll/tax-slabs', slabData);
    return { data };
  },

  // --- Tax Deduction Types ---
  getTaxDeductionTypes: async (activeOnly = true): Promise<{ data: TaxDeductionType[] }> => {
    const data = await api.get(`/payroll/tax-deduction-types?active_only=${activeOnly}`);
    return { data };
  },

  createTaxDeductionType: async (
    typeData: Omit<TaxDeductionType, 'id'>
  ): Promise<{ data: TaxDeductionType }> => {
    const data = await api.post('/payroll/tax-deduction-types', typeData);
    return { data };
  },

  // --- Employee Tax Deductions ---
  getEmployeeTaxDeductions: async (
    employeeId: string,
    taxYear: string
  ): Promise<{ data: EmployeeTaxDeduction[] }> => {
    const data = await api.get(`/employees/${employeeId}/tax-deductions?tax_year=${taxYear}`);
    return { data };
  },

  createEmployeeTaxDeduction: async (
    employeeId: string,
    deductionData: {
      deductionTypeId: string;
      taxYear: string;
      claimedAmount: number;
      numberOfChildren?: number;
      institutionName?: string;
      institutionNtn?: string;
    }
  ): Promise<{ data: EmployeeTaxDeduction }> => {
    const data = await api.post(`/employees/${employeeId}/tax-deductions`, deductionData);
    return { data };
  },

  deleteEmployeeTaxDeduction: async (employeeId: string, deductionId: number): Promise<void> => {
    await api.delete(`/employees/${employeeId}/tax-deductions/${deductionId}`);
  },

  // --- Tax Calculation ---
  getTaxCalculation: async (
    employeeId: string,
    taxYear: string
  ): Promise<{ data: TaxCalculationDetail }> => {
    const data = await api.get(`/payroll/tax-calculation/${employeeId}/${taxYear}`);
    return { data };
  },

  // --- Employee Salary Structure ---
  getEmployeeSalaryStructure: async (
    employeeId: string
  ): Promise<{ data: EmployeeSalaryStructure[] }> => {
    const data = await api.get(`/employees/${employeeId}/salary-structure`);
    return { data };
  },

  setEmployeeSalaryStructure: async (
    employeeId: string,
    structureData: {
      componentId: string;
      amount: number;
      percentage?: number;
      effectiveFrom: string;
      effectiveTo?: string;
    }
  ): Promise<{ data: EmployeeSalaryStructure }> => {
    const data = await api.put(`/employees/${employeeId}/salary-structure`, structureData);
    return { data };
  },

  // --- Payroll Runs ---
  getPayrollRuns: async (skip = 0, limit = 50): Promise<{ data: PayrollRun[] }> => {
    const data = await api.get(`/payroll/runs?skip=${skip}&limit=${limit}`);
    return { data };
  },

  createPayrollRun: async (runData: {
    periodMonth: string;
    periodYear: string;
    notes?: string;
  }): Promise<{ data: PayrollRun }> => {
    const data = await api.post('/payroll/runs', runData);
    return { data };
  },

  processPayrollRun: async (runId: string): Promise<{ data: PayrollRun }> => {
    const data = await api.post(`/payroll/runs/${runId}/process`);
    return { data };
  },

  finalizePayrollRun: async (
    runId: string,
    paymentMode = 'Bank Transfer'
  ): Promise<{ data: PayrollRun }> => {
    const data = await api.post(
      `/payroll/runs/${runId}/finalize?payment_mode=${encodeURIComponent(paymentMode)}`
    );
    return { data };
  },

  getPayrollRunDetails: async (
    runId: string,
    skip = 0,
    limit = 100
  ): Promise<{ data: PayslipDetail[] }> => {
    const data = await api.get(`/payroll/runs/${runId}/details?skip=${skip}&limit=${limit}`);
    return { data };
  },

  // --- Payslips ---
  getEmployeePayslip: async (
    employeeId: string,
    periodMonth: string,
    periodYear: string
  ): Promise<{ data: PayslipDetail }> => {
    const data = await api.get(`/payroll/payslips/${employeeId}/${periodMonth}/${periodYear}`);
    return { data };
  },

  downloadPayslipPdf: (employeeId: string, periodMonth: string, periodYear: string) => {
    const baseUrl = API_CONFIG.BASE_URL;
    const url = `${baseUrl}/payroll/payslips/${employeeId}/${periodMonth}/${periodYear}/pdf`;
    window.open(url, '_blank');
  },
};
