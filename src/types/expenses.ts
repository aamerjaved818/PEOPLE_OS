export type ExpenseStatus = 'Pending' | 'Approved' | 'Flagged' | 'Paid' | 'Rejected';
export type ExpenseCategory =
  | 'Travel'
  | 'Meals'
  | 'Equipment'
  | 'Utility'
  | 'Accommodation'
  | 'Transport'
  | 'Professional Dev'
  | 'Other';

export interface Expense {
  id: string;
  employeeName: string;
  category: ExpenseCategory;
  amount: number;
  currency: string;
  date: string;
  status: ExpenseStatus;
  receiptUrl?: string;
}
