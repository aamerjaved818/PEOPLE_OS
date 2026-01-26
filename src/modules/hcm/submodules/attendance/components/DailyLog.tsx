import React from 'react';
import { Camera, Search, Filter, ScanFace, Globe, MapPin } from 'lucide-react';
import { AttendanceRecord } from '@/types';
import { VibrantBadge } from '@/components/ui/VibrantBadge';

interface DailyLogProps {
  searchTerm: string;
  setSearchTerm: (value: string) => void;
  filteredRecords: AttendanceRecord[];
  isLoading: boolean;
}

export const DailyLog: React.FC<DailyLogProps> = ({
  searchTerm,
  setSearchTerm,
  filteredRecords,
  isLoading,
}) => {
  return (
    <div className="space-y-10 animate-in fade-in duration-500">
      <div className="bg-surface rounded-md border border-border shadow-md overflow-hidden min-h-[37.5rem] flex flex-col">
        <div className="p-12 border-b border-border flex flex-col lg:flex-row lg:items-center justify-between gap-10 bg-muted-bg/30 backdrop-blur-3xl">
          <div>
            <h3 className="text-3xl font-black text-text-primary tracking-tight">
              Daily Attendance Log
            </h3>
            <p className="text-[0.625rem] font-black text-text-muted uppercase tracking-widest mt-2 flex items-center gap-2">
              <Camera size={12} className="text-primary" /> Facial Verification Active
            </p>
          </div>
          <div className="flex gap-4">
            <div className="relative group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted group-focus-within:text-primary transition-colors" />
              <input
                aria-label="Search employees"
                className="bg-app border border-border pl-10 pr-6 py-3 rounded-md text-sm font-black outline-none w-64 text-text-primary shadow-inner"
                placeholder="Search Employees..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button
              aria-label="Filter records"
              className="flex items-center gap-3 px-6 py-3 bg-muted-bg rounded-md text-text-muted hover:text-primary transition-all shadow-sm font-black uppercase text-[0.625rem] tracking-widest"
            >
              <Filter size={16} /> Filter
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-muted-bg/50">
                <th className="px-14 py-8 text-[0.6875rem] font-black text-text-muted uppercase tracking-[0.25em]">
                  Employee
                </th>
                <th className="px-8 py-8 text-[0.6875rem] font-black text-text-muted uppercase tracking-[0.25em]">
                  Shift
                </th>
                <th className="px-8 py-8 text-[0.6875rem] font-black text-text-muted uppercase tracking-[0.25em]">
                  Time Log
                </th>
                <th className="px-8 py-8 text-[0.6875rem] font-black text-text-muted uppercase tracking-[0.25em]">
                  Status
                </th>
                <th className="px-8 py-8 text-[0.6875rem] font-black text-text-muted uppercase tracking-[0.25em]">
                  Verification
                </th>
                <th className="px-14 py-8 text-right text-[0.6875rem] font-black text-text-muted uppercase tracking-[0.25em]">
                  Location
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-14 py-8 text-center text-text-muted">
                    Loading attendance records...
                  </td>
                </tr>
              ) : filteredRecords.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-14 py-8 text-center text-text-muted">
                    No records found.
                  </td>
                </tr>
              ) : (
                filteredRecords.map((row, index) => (
                  <tr
                    key={row.id}
                    className="group hover:bg-primary-soft/50 transition-all cursor-pointer font-mono animate-in slide-in-from-bottom-2 duration-500"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <td className="px-14 py-8 font-sans">
                      <p className="text-lg font-black text-text-primary leading-none">
                        {row.employeeName}
                      </p>
                      <p className="text-[0.625rem] font-black text-primary uppercase tracking-widest mt-2">
                        {row.employeeCode}
                      </p>
                    </td>
                    <td className="px-8 py-8">
                      <VibrantBadge color="purple" variant="outline" className="font-black">
                        Shift {row.shiftName}
                      </VibrantBadge>
                    </td>
                    <td className="px-8 py-8 space-y-1">
                      <p className="text-sm font-black text-text-muted">
                        In: <span className="text-primary">{row.clockIn}</span>
                      </p>
                      <p className="text-sm font-black text-text-muted">
                        Out: <span className="text-primary">{row.clockOut}</span>
                      </p>
                    </td>
                    <td className="px-8 py-8">
                      <VibrantBadge>{row.status}</VibrantBadge>
                    </td>
                    <td className="px-8 py-8">
                      <div className="flex items-center gap-2">
                        {row.verificationType === 'Facial' ? (
                          <ScanFace className="text-primary" size={16} />
                        ) : (
                          <Globe className="text-success" size={16} />
                        )}
                        <span className="text-[0.625rem] font-black uppercase text-text-muted">
                          {row.verificationType} ID
                        </span>
                      </div>
                    </td>
                    <td className="px-14 py-8 text-right font-sans">
                      <div className="flex items-center justify-end gap-3 text-[0.625rem] font-black text-text-muted uppercase">
                        <MapPin className="w-4 h-4 text-primary" />
                        {row.location}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
