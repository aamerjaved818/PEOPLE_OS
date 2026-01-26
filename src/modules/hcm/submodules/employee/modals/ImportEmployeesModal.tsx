import React, { useState } from 'react';
import { Upload, CheckCircle, AlertTriangle } from 'lucide-react';
import { importFromExcel } from '@/utils/exportUtils';
import { Button } from '@/components/ui/Button';
import { Employee as EmployeeType } from '@/types';
import { api } from '@/services/api';
import { useToast } from '@/components/ui/Toast';
import Modal from '@/components/ui/Modal';
import { EMPLOYEE_CODE } from '@/config';

interface ImportEmployeesModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportComplete: () => void;
}

export const ImportEmployeesModal: React.FC<ImportEmployeesModalProps> = ({
  isOpen,
  onClose,
  onImportComplete,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [data, setData] = useState<any[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const { success, error } = useToast();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);

      try {
        const jsonData = await importFromExcel(selectedFile);
        setData(jsonData);
      } catch (err) {
        error('Failed to parse Excel file');
        console.error(err);
      }
    }
  };

  const processImport = async () => {
    if (!data.length) {
      return;
    }

    setIsProcessing(true);
    let successCount = 0;
    let failCount = 0;

    for (let i = 0; i < data.length; i++) {
      const row = data[i];
      // Basic mapping - assumes specific headers or loose matching
      // Default to "Unknown" if missing
      const newEmp: Partial<EmployeeType> = {
        id: row['ID'] || row['Employee ID'] || `${EMPLOYEE_CODE.PREFIX}-${Date.now()}-${i}`,
        employeeCode: row['Code'] || row['Employee Code'] || `${EMPLOYEE_CODE.PREFIX}-IMP-${i}`,
        name: row['Name'] || row['Full Name'] || 'Unknown Import',
        designation: row['Designation'] || 'N/A',
        department: row['Department'] || 'N/A',
        status: 'Active',
        joiningDate: new Date().toISOString().split('T')[0], // Default to today
        // Add more mappings as needed
        grossSalary: Number(row['Salary'] || row['Gross Salary'] || 0),
        personalEmail: row['Email'] || '',
        personalCellNumber: row['Phone'] || '',

        // Required fields with defaults
        maritalStatus: 'Single',
        religion: 'Islam',
        nationality: 'Pakistani',
        paymentMode: 'Cash Payment',
        socialSecurityStatus: false,
        eobiStatus: false,
        medicalStatus: false,
        family: [],
        education: [],
        experience: [],
        increments: [],
        discipline: [],
      };

      try {
        await api.saveEmployee(newEmp as EmployeeType);
        successCount++;
      } catch (err) {
        console.error(`Failed to import row ${i}:`, err);
        failCount++;
      }

      setProgress(Math.round(((i + 1) / data.length) * 100));
    }

    setIsProcessing(false);
    success(`Import Processed: ${successCount} Success, ${failCount} Failed`);
    onImportComplete();
    onClose();

    // Reset state
    setFile(null);
    setData([]);
    setProgress(0);
  };

  return (
    <Modal title="Import Employees" isOpen={isOpen} onClose={onClose} size="md">
      <div className="space-y-6">
        {/* Drag & Drop Area */}
        <div className="border-2 border-dashed border-border rounded-xl p-8 flex flex-col items-center justify-center bg-surface/50 hover:bg-surface hover:border-primary/50 transition-all group cursor-pointer relative">
          <input
            type="file"
            accept=".xlsx, .xls"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="p-4 bg-primary/10 rounded-full mb-4 group-hover:scale-110 transition-transform">
            <Upload className="w-8 h-8 text-primary" />
          </div>
          <p className="font-bold text-text-primary">Click to Upload Excel File</p>
          <p className="text-xs text-text-muted mt-2">.xlsx or .xls files supported</p>
          {file && (
            <div className="mt-4 px-4 py-2 bg-success/10 text-success rounded-lg text-xs font-bold flex items-center gap-2">
              <CheckCircle size={14} />
              {file.name} ({data.length} records found)
            </div>
          )}
        </div>

        {/* Warning */}
        <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-bold text-amber-500 uppercase tracking-wider mb-1">
              Important Note
            </p>
            <p className="text-xs text-text-secondary/80 leading-relaxed">
              Please ensure your Excel file has proper headers.
              <button
                onClick={async () => {
                  const { exportToExcel } = await import('@/utils/exportUtils');
                  const sampleData = [
                    {
                      'Employee ID': 'EMP-001',
                      'Employee Code': 'EMP-001',
                      'Full Name': 'John Doe',
                      'Father Name': 'Richard Doe',
                      Gender: 'Male',
                      'Date of Birth': '01-Jan-1990',
                      CNIC: '12345-1234567-1',
                      'CNIC Expiry': '01-Jan-2030',
                      Religion: 'Islam',
                      'Marital Status': 'Single',
                      'Blood Group': 'O+',
                      Nationality: 'Pakistani',
                      Designation: 'Software Engineer',
                      Grade: 'G-01',
                      Department: 'IT',
                      'Sub Department': 'Development',
                      'Plant/Location': 'Head Office',
                      Shift: 'General',
                      'Rest Day': 'Sunday',
                      'Employment Status': 'Active',
                      'Joining Date': '01-Jan-2024',
                      'Confirmation Date': '',
                      'Probation Period': '3 Months',
                      'Separation Date': '',
                      'Separation Type': '',
                      'Personal Phone': '0300-1234567',
                      'Official Phone': '',
                      'Personal Email': 'john@example.com',
                      'Official Email': '',
                      'Present Address': '123 Street, City',
                      'Permanent Address': '123 Street, City',
                      'City/District': 'Lahore',
                      'Gross Salary': 100000,
                      'Payment Mode': 'Bank Transfer',
                      'Bank Name': 'HBL',
                      'Account Number': '1234567890',
                      'EOBI Number': '12345',
                      'Social Security': '67890',
                      'House Rent': 0,
                      'Utility Allowance': 0,
                    },
                  ];
                  exportToExcel(sampleData, 'Employee_Import_Template');
                }}
                className="ml-1 text-primary hover:underline font-bold"
              >
                Download Sample Template
              </button>
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        {isProcessing && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-bold uppercase text-text-muted">
              <span>Processing...</span>
              <span>{progress}%</span>
            </div>
            <div className="h-2 bg-surface border border-border rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        <div className="flex justify-end gap-3 pt-4 border-t border-border/10">
          <Button variant="secondary" onClick={onClose} disabled={isProcessing}>
            Cancel
          </Button>
          <Button onClick={processImport} disabled={!file || isProcessing || data.length === 0}>
            {isProcessing ? 'Importing...' : 'Start Import'}
          </Button>
        </div>
      </div>
    </Modal>
  );
};
