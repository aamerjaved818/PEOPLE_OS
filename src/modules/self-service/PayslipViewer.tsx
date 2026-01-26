/**
 * Payslip Viewer
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { selfServiceApi } from '@/services/selfServiceApi';
import { API_CONFIG } from '@/config/constants';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export const PayslipViewer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  const [selectedYear, setSelectedYear] = useState(currentYear);
  const [selectedMonth, setSelectedMonth] = useState<string | undefined>();

  const { data: payslips, isLoading } = useQuery({
    queryKey: ['myPayslips', selectedYear, selectedMonth],
    queryFn: () => selfServiceApi.getMyPayslips(selectedYear, selectedMonth),
  });

  const years = Array.from({ length: 3 }, (_, i) => currentYear - i);
  const months = [
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

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">My Payslips</h1>

      {/* Filters */}
      <Card className="mb-6">
        <div className="p-4 flex items-center space-x-4">
          <div>
            <label className="block text-sm font-medium mb-2">Year</label>
            <select
              className="border rounded-md p-2"
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
            >
              {years.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Month (Optional)</label>
            <select
              className="border rounded-md p-2"
              value={selectedMonth || ''}
              onChange={(e) => setSelectedMonth(e.target.value || undefined)}
            >
              <option value="">All Months</option>
              {months.map((month) => (
                <option key={month} value={month}>
                  {month}
                </option>
              ))}
            </select>
          </div>

          {selectedMonth && (
            <Button variant="outline" onClick={() => setSelectedMonth(undefined)} className="mt-6">
              Clear Filter
            </Button>
          )}
        </div>
      </Card>

      {/* Payslips List */}
      {isLoading ? (
        <div className="text-center py-12">Loading...</div>
      ) : payslips && payslips.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {payslips.map((payslip: any) => (
            <Card key={payslip.id} className="hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-3xl">💵</span>
                  <span className="text-sm font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full">
                    {payslip.period_month} {payslip.period_year}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Gross Salary:</span>
                    <span className="font-semibold">
                      PKR {payslip.gross_salary?.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Net Salary:</span>
                    <span className="font-semibold text-green-600">
                      PKR {payslip.net_salary?.toLocaleString()}
                    </span>
                  </div>
                </div>

                <Button
                  className="w-full"
                  variant="outline"
                  onClick={() =>
                    window.open(`${API_CONFIG.BASE_URL}/payroll/${payslip.id}/pdf`, '_blank')
                  }
                >
                  View Payslip
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <div className="p-12 text-center">
            <p className="text-gray-500 text-lg">No payslips found</p>
            <p className="text-sm text-gray-400 mt-2">
              {selectedMonth
                ? `No payslips for ${selectedMonth} ${selectedYear}`
                : `No payslips for ${selectedYear}`}
            </p>
          </div>
        </Card>
      )}
    </div>
  );
};
