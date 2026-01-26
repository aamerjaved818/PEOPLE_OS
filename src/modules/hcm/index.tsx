import React, { useState, Suspense } from 'react';
import { DetailLayout } from '@/components/layout/DetailLayout';
import {
  Users,
  Briefcase,
  UserPlus,
  Rocket,
  LogOut,
  Clock,
  CalendarRange,
  Timer,
} from 'lucide-react';
import { HorizontalTabs } from '@/components/ui/HorizontalTabs';
import ModuleSkeleton from '@/components/ui/ModuleSkeleton';
import ErrorBoundary from '@/components/ErrorBoundary';
import { useTheme } from '@/contexts/ThemeContext';

// Lazy Load Sub-components
const Employees = React.lazy(() => import('./submodules/employee/EmployeeSubmodule'));
const RecruitmentATS = React.lazy(() => import('./submodules/recruitment/RecruitmentSubmodule'));
const JobPostings = React.lazy(() => import('./submodules/job-postings/JobPostingsSubmodule'));
const Onboarding = React.lazy(() => import('./submodules/onboarding/OnboardingSubmodule'));
const Offboarding = React.lazy(() => import('./submodules/offboarding/OffboardingSubmodule'));
const Attendance = React.lazy(() => import('./submodules/attendance/AttendanceSubmodule'));
const Leaves = React.lazy(() => import('./submodules/leaves/LeavesSubmodule'));
const Overtime = React.lazy(() => import('./submodules/overtime/OvertimeSubmodule'));

const HCMModule: React.FC = () => {
  const { theme } = useTheme();
  void theme;
  const [activeSection, setActiveSection] = useState('employees');

  const sections = [
    { id: 'employees', label: 'Employee Directory', icon: Users },
    { id: 'recruitment', label: 'Recruitment (ATS)', icon: UserPlus },
    { id: 'job-postings', label: 'Job Postings', icon: Briefcase },
    { id: 'onboarding', label: 'Onboarding', icon: Rocket },
    { id: 'offboarding', label: 'Offboarding', icon: LogOut },
    { id: 'attendance', label: 'Attendance', icon: Clock },
    { id: 'leaves', label: 'Leave Mgmt', icon: CalendarRange },
    { id: 'overtime', label: 'Overtime', icon: Timer },
  ];

  return (
    <DetailLayout
      className="animate-in fade-in duration-500"
      containerClassName="max-w-[1400px]"
      header={null}
      tabs={
        <div className="max-w-[1400px] mx-auto px-6 pt-2 pb-0">
          <HorizontalTabs
            tabs={sections}
            activeTabId={activeSection}
            onTabChange={setActiveSection}
            wrap={true}
            align="start"
            className="mb-0 border-b-0"
          />
        </div>
      }
    >
      <Suspense fallback={<ModuleSkeleton />}>
        {activeSection === 'employees' && <Employees />}
        {activeSection === 'recruitment' && <RecruitmentATS />}
        {activeSection === 'job-postings' && <JobPostings />}
        {activeSection === 'onboarding' && <Onboarding />}
        {activeSection === 'offboarding' && <Offboarding />}
        {activeSection === 'attendance' && <Attendance />}
        {activeSection === 'leaves' && <Leaves />}
        {activeSection === 'overtime' && <Overtime />}
      </Suspense>
    </DetailLayout>
  );
};

const HCMModuleWithBoundary: React.FC = () => (
  <ErrorBoundary>
    <HCMModule />
  </ErrorBoundary>
);

export default HCMModuleWithBoundary;
