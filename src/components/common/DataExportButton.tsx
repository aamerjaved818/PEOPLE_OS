import React, { useState } from 'react';
import { Download, FileSpreadsheet, FileText } from 'lucide-react';
import ExcelJS from 'exceljs';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { Button } from '@/components/ui/Button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/DropdownMenu';

export interface ExportColumn {
  key: string;
  header: string;
}

interface DataExportButtonProps {
  data: any[];
  columns: ExportColumn[];
  filename: string;
  title: string;
  className?: string; // Allow custom styling
}

export const DataExportButton: React.FC<DataExportButtonProps> = ({
  data,
  columns,
  filename,
  title,
  className,
}) => {
  const [isExporting, setIsExporting] = useState(false);

  // Helper to extract nested values (e.g., 'department.name')
  const getValue = (obj: any, path: string) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], obj);
  };

  const handleExportExcel = async () => {
    try {
      setIsExporting(true);
      const workbook = new ExcelJS.Workbook();
      const worksheet = workbook.addWorksheet('Data');

      // Define Columns
      worksheet.columns = columns.map((col) => ({
        header: col.header,
        key: col.key,
        width: 20,
      }));

      // Add Rows
      data.forEach((item) => {
        const rowData: Record<string, any> = {};
        columns.forEach((col) => {
          const val = getValue(item, col.key);
          // Handle arrays or objects gracefully if needed, for now simplistic string
          rowData[col.key] = val !== null && val !== undefined ? String(val) : '';
        });
        worksheet.addRow(rowData);
      });

      // Style Header
      worksheet.getRow(1).font = { bold: true };

      // Write Buffer
      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });

      // Save
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `${filename}.xlsx`;
      anchor.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Excel export failed', error);
      alert('Failed to export to Excel');
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportPDF = () => {
    try {
      setIsExporting(true);
      const doc = new jsPDF();

      // Title
      doc.setFontSize(18);
      doc.text(title, 14, 22);
      doc.setFontSize(11);
      doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 14, 30);

      // Table Data
      const tableColumn = columns.map((col) => col.header);
      const tableRows = data.map((item) => {
        return columns.map((col) => {
          const val = getValue(item, col.key);
          return val !== null && val !== undefined ? String(val) : '';
        });
      });

      autoTable(doc, {
        head: [tableColumn],
        body: tableRows,
        startY: 40,
        styles: { fontSize: 8 },
        headStyles: { fillColor: [66, 133, 244] }, // Google Blue :)
      });

      doc.save(`${filename}.pdf`);
    } catch (error) {
      console.error('PDF export failed', error);
      alert('Failed to export to PDF');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={`h-9 border-dashed ${className}`}
          disabled={isExporting}
        >
          <Download size={16} className="mr-2" />
          {isExporting ? 'Exporting...' : 'Export'}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem onClick={handleExportExcel} className="cursor-pointer">
          <FileSpreadsheet className="mr-2 h-4 w-4 text-green-600" />
          <span>Export to Excel</span>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleExportPDF} className="cursor-pointer">
          <FileText className="mr-2 h-4 w-4 text-red-600" />
          <span>Export to PDF</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
