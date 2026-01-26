/**
 * PayslipViewer - View and download monthly payslips
 * Shows earnings vs deductions breakdown with PDF download
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Download, DollarSign, TrendingUp, TrendingDown, RefreshCw, FileText } from 'lucide-react';
import { payrollApi, PayslipDetail } from '@/services/payrollApi';
import { formatCurrency } from '@/utils/formatting';

interface PayslipViewerProps {
  employeeId: string;
}

const MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

const PayslipViewer: React.FC<PayslipViewerProps> = ({ employeeId }) => {
  const [payslip, setPayslip] = useState<PayslipDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(MONTHS[new Date().getMonth()]);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear().toString());

  const loadPayslip = useCallback(async () => {
    try {
      setLoading(true);
      const response = await payrollApi.getEmployeePayslip(employeeId, selectedMonth, selectedYear);
      setPayslip(response.data);
    } catch (error) {
      console.error('Failed to load payslip:', error);
      setPayslip(null);
    } finally {
      setLoading(false);
    }
  }, [employeeId, selectedMonth, selectedYear]);

  useEffect(() => {
    if (selectedMonth && selectedYear) {
      loadPayslip();
    }
  }, [loadPayslip, selectedMonth, selectedYear]);

  const handleDownloadPdf = () => {
    payrollApi.downloadPayslipPdf(employeeId, selectedMonth, selectedYear);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-text-primary tracking-tight">My Payslips</h1>
          <p className="text-sm text-text-muted mt-1">View and download your salary slips</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
          >
            {MONTHS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
          <input
            type="text"
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
            className="w-20 px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
          />
        </div>
      </div>

      {loading ? (
        <div className="bg-surface rounded-xl border border-border p-12 text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-text-muted">Loading payslip...</p>
        </div>
      ) : !payslip ? (
        <div className="bg-surface rounded-xl border border-border p-12 text-center">
          <FileText className="w-12 h-12 mx-auto mb-4 text-text-muted opacity-30" />
          <p className="text-text-muted">
            No payslip found for {selectedMonth} {selectedYear}
          </p>
        </div>
      ) : (
        <div className="bg-surface rounded-xl border border-border shadow-lg overflow-hidden">
          {/* Header Section */}
          <div className="bg-gradient-to-r from-primary to-primary/80 p-6 text-white">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-xl font-black">Payslip</h2>
                <p className="opacity-80">
                  {selectedMonth} {selectedYear}
                </p>
              </div>
              <button
                onClick={handleDownloadPdf}
                className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg font-bold transition-colors"
              >
                <Download className="w-4 h-4" />
                Download PDF
              </button>
            </div>
            <div className="mt-4 pt-4 border-t border-white/20">
              <p className="font-bold text-lg">{payslip.employeeName}</p>
              <p className="opacity-80 text-sm">{payslip.employeeCode}</p>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Earnings */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-5 h-5 text-success" />
                  <h3 className="font-black text-text-primary uppercase tracking-wider text-sm">
                    Earnings
                  </h3>
                </div>
                <div className="space-y-3">
                  {[
                    { label: 'Basic Salary', value: payslip.basicSalary },
                    { label: 'House Rent', value: payslip.houseRent },
                    { label: 'Medical Allowance', value: payslip.medicalAllowance },
                    { label: 'Transport Allowance', value: payslip.transportAllowance },
                    { label: 'Other Allowances', value: payslip.otherAllowances },
                  ].map((item, i) => (
                    <div
                      key={i}
                      className="flex justify-between items-center py-2 border-b border-border/50"
                    >
                      <span className="text-text-muted">{item.label}</span>
                      <span className="font-mono font-bold text-text-primary">
                        {formatCurrency(item.value)}
                      </span>
                    </div>
                  ))}
                  <div className="flex justify-between items-center py-3 bg-success/10 rounded-lg px-3 mt-2">
                    <span className="font-bold text-success">Gross Salary</span>
                    <span className="font-mono font-black text-success text-lg">
                      {formatCurrency(payslip.grossSalary)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Deductions */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <TrendingDown className="w-5 h-5 text-danger" />
                  <h3 className="font-black text-text-primary uppercase tracking-wider text-sm">
                    Deductions
                  </h3>
                </div>
                <div className="space-y-3">
                  {[
                    { label: 'Income Tax', value: payslip.incomeTax },
                    { label: 'EOBI', value: payslip.eobiDeduction },
                    { label: 'Social Security', value: payslip.socialSecurity },
                    { label: 'Loan Deduction', value: payslip.loanDeduction },
                    { label: 'Other Deductions', value: payslip.otherDeductions },
                  ].map((item, i) => (
                    <div
                      key={i}
                      className="flex justify-between items-center py-2 border-b border-border/50"
                    >
                      <span className="text-text-muted">{item.label}</span>
                      <span className="font-mono font-bold text-danger">
                        {formatCurrency(item.value)}
                      </span>
                    </div>
                  ))}
                  <div className="flex justify-between items-center py-3 bg-danger/10 rounded-lg px-3 mt-2">
                    <span className="font-bold text-danger">Total Deductions</span>
                    <span className="font-mono font-black text-danger text-lg">
                      {formatCurrency(payslip.totalDeductions)}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Net Salary */}
            <div className="mt-8 p-6 bg-gradient-to-r from-primary/10 to-success/10 rounded-xl border border-primary/20">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <DollarSign className="w-8 h-8 text-primary" />
                  <div>
                    <p className="text-sm text-text-muted uppercase tracking-wider font-bold">
                      Net Salary Payable
                    </p>
                    <p className="text-3xl font-black text-primary">
                      {formatCurrency(payslip.netSalary)}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-text-muted uppercase tracking-wider">Status</p>
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-sm font-bold mt-1 ${
                      payslip.status === 'Paid'
                        ? 'bg-success/20 text-success'
                        : 'bg-warning/20 text-warning'
                    }`}
                  >
                    {payslip.status}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PayslipViewer;
