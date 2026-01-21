import React from 'react';
import {
  Briefcase,
  Calendar,
  MapPin,
  User,
  DollarSign,
  Clock,
  Building2,
  ShieldCheck,
} from 'lucide-react';
import { Employee } from '../../types';

interface DashboardTabProps {
  employee: Partial<Employee> | null;
}

const DashboardTab: React.FC<DashboardTabProps> = ({ employee }) => {
  if (!employee) {
    return null;
  }

  const stats = [
    {
      label: 'Department',
      value: employee.department || 'Not Assigned',
      icon: Building2,
      color: 'text-blue-500',
    },
    {
      label: 'Designation',
      value: employee.designation || 'Not Assigned',
      icon: Briefcase,
      color: 'text-purple-500',
    },
    {
      label: 'Plant',
      value: employee.hrPlant || 'Not Assigned',
      icon: MapPin,
      color: 'text-green-500',
    },
    {
      label: 'Joining Date',
      value: employee.joiningDate || 'Not Set',
      icon: Calendar,
      color: 'text-orange-500',
    },
    {
      label: 'Status',
      value: employee.status || 'Active',
      icon: ShieldCheck,
      color: 'text-emerald-500',
    },
    {
      label: 'Gross Salary',
      value: employee.grossSalary ? `PKR ${employee.grossSalary.toLocaleString()}` : 'Not Set',
      icon: DollarSign,
      color: 'text-rose-500',
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Quick Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="bg-surface p-6 rounded-2xl border border-border hover:border-primary/30 transition-all group"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[0.625rem] font-black text-text-muted uppercase tracking-widest mb-1">
                  {stat.label}
                </p>
                <p className="text-lg font-bold text-text-primary group-hover:text-primary transition-colors">
                  {stat.value}
                </p>
              </div>
              <div className={`p-3 rounded-xl bg-muted-bg ${stat.color}`}>
                <stat.icon size={20} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Profile Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-surface p-8 rounded-3xl border border-border space-y-6">
          <h3 className="text-xl font-black text-text-primary tracking-tight flex items-center gap-3">
            <User size={24} className="text-primary" />
            Personal Highlights
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between py-3 border-b border-border/50">
              <span className="text-sm font-bold text-text-secondary uppercase tracking-wider">
                Employee Code
              </span>
              <span className="text-sm font-black text-primary">{employee.employeeCode}</span>
            </div>
            <div className="flex justify-between py-3 border-b border-border/50">
              <span className="text-sm font-bold text-text-secondary uppercase tracking-wider">
                Blood Group
              </span>
              <span className="text-sm font-black">{employee.bloodGroup || 'O+'}</span>
            </div>
            <div className="flex justify-between py-3 border-b border-border/50">
              <span className="text-sm font-bold text-text-secondary uppercase tracking-wider">
                Marital Status
              </span>
              <span className="text-sm font-black">{employee.maritalStatus}</span>
            </div>
            <div className="flex justify-between py-3 border-b border-border/50">
              <span className="text-sm font-bold text-text-secondary uppercase tracking-wider">
                Religion
              </span>
              <span className="text-sm font-black">{employee.religion || 'Islam'}</span>
            </div>
          </div>
        </div>

        <div className="bg-surface p-8 rounded-3xl border border-border space-y-6">
          <h3 className="text-xl font-black text-text-primary tracking-tight flex items-center gap-3">
            <Clock size={24} className="text-primary" />
            Employment Timeline
          </h3>
          <div className="relative pl-8 space-y-8 before:content-[''] before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[2px] before:bg-border">
            <div className="relative">
              <div className="absolute -left-[27px] top-1 w-4 h-4 rounded-full bg-primary border-4 border-surface" />
              <p className="text-xs font-black text-text-muted uppercase tracking-widest leading-none mb-2">
                Joined Company
              </p>
              <p className="text-sm font-black text-text-primary">{employee.joiningDate}</p>
            </div>
            <div className="relative opacity-50">
              <div className="absolute -left-[27px] top-1 w-4 h-4 rounded-full bg-border border-4 border-surface" />
              <p className="text-xs font-black text-text-muted uppercase tracking-widest leading-none mb-2">
                Probation End
              </p>
              <p className="text-sm font-black text-text-primary">Calculating...</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardTab;
