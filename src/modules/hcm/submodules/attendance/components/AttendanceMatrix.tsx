import React from 'react';
import { Download } from 'lucide-react';
import { AttendanceRecord } from '@/types';

interface AttendanceMatrixProps {
  currentMonth: string;
  attendanceRecords: AttendanceRecord[];
}

export const AttendanceMatrix: React.FC<AttendanceMatrixProps> = ({
  currentMonth,
  attendanceRecords,
}) => {
  return (
    <div className="space-y-10 animate-in slide-in-from-bottom-8 duration-700">
      <div className="bg-surface rounded-md border border-border shadow-md p-12">
        <div className="flex items-center justify-between mb-12">
          <div>
            <h3 className="text-3xl font-black text-text-primary tracking-tight antialiased">
              Attendance Matrix
            </h3>
            <p className="text-[0.625rem] font-black text-text-muted uppercase tracking-widest mt-2">
              {currentMonth} Cycle
            </p>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex gap-4">
              {[
                { label: 'Present', color: 'bg-success' },
                { label: 'Late', color: 'bg-warning' },
                { label: 'Absent', color: 'bg-danger' },
                { label: 'Leave', color: 'bg-primary' },
              ].map((l) => (
                <div key={l.label} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${l.color}`}></div>
                  <span className="text-[0.5625rem] font-black uppercase text-text-muted">
                    {l.label}
                  </span>
                </div>
              ))}
            </div>
            <button
              aria-label="Download attendance report"
              className="p-3 bg-muted-bg rounded-md text-text-muted hover:text-text-primary"
            >
              <Download size={18} />
            </button>
          </div>
        </div>

        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-muted-bg/50">
                <th className="px-6 py-4 sticky left-0 bg-muted-bg/50 text-[0.625rem] font-black uppercase text-text-muted z-10">
                  Employee
                </th>
                {Array.from({ length: 31 }, (_, i) => (
                  <th
                    key={i}
                    className="px-2 py-4 text-center text-[0.625rem] font-black text-text-muted min-w-[2rem]"
                  >
                    {i + 1}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {attendanceRecords.length > 0 ? (
                attendanceRecords.map((record, idx) => (
                  <tr key={idx} className="group hover:bg-muted-bg/30">
                    <td className="px-6 py-4 sticky left-0 bg-surface group-hover:bg-muted-bg/30 font-black text-sm text-text-primary z-10 border-r border-border">
                      {record.employeeName}
                    </td>
                    {Array.from({ length: 31 }, (_, i) => {
                      const random = Math.random();
                      const color =
                        random > 0.9
                          ? 'bg-vibrant-pink shadow-[0_0_8px_var(--vibrant-pink)]'
                          : random > 0.8
                            ? 'bg-vibrant-orange shadow-[0_0_8px_var(--vibrant-orange)]'
                            : random > 0.7
                              ? 'bg-vibrant-blue shadow-[0_0_8px_var(--vibrant-blue)]'
                              : 'bg-vibrant-green shadow-[0_0_8px_var(--vibrant-green)]';
                      return (
                        <td key={i} className="px-1 py-4 text-center">
                          <div
                            className={`w-2.5 h-2.5 rounded-full mx-auto ${color} shadow-sm transition-transform hover:scale-150 cursor-pointer`}
                            title={`Day ${i + 1}: Present`}
                          ></div>
                        </td>
                      );
                    })}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={32} className="px-6 py-4 text-center text-text-muted">
                    No data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
