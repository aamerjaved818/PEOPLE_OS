export interface PayrollSettings {
  overtimeEnabled: boolean;
  taxYearEnd: string;
  currency: string;
  calculationMethod: 'Per Month' | 'Per Day' | 'User Defined' | '';
  customFormulas: {
    staff: string;
    worker: string;
  };
  overtime: {
    routine: {
      staff: string;
      worker: string;
    };
    gazetteHoliday: {
      staff: string;
      worker: string;
    };
  };
}

export interface PayrollRecord {
  id: string;
  name: string;
  employeeId: string;
  dept: string;
  basicSalary: number;
  allowances: number;
  gross: number;
  tax: number;
  deductions: number;
  net: number;
  status: 'Pending' | 'Processed' | 'Paid' | 'Flagged';
  paymentDate?: string;
  paymentMode?: string;
  bankName?: string;
  accountNumber?: string;
  month: string;
}
