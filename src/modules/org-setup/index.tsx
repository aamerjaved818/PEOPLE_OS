import React, { useState } from 'react';
import { Building, Users, Factory, Briefcase, Network } from 'lucide-react';
import { HorizontalTabs } from '@/components/ui/HorizontalTabs';
import ErrorBoundary from '@/components/ErrorBoundary';
import { DetailLayout } from '@/components/layout/DetailLayout';

// Components
import OrgProfile from './OrgProfile';
import DepartmentManagement from './DepartmentManagement';
import DesignationManagement from './DesignationManagement';
import PlantManagement from './PlantManagement';
import JobLevelManagement from './JobLevelManagement';
import HierarchyChart from './HierarchyChart';
import LeadershipManagement from './LeadershipManagement';

import { useTheme } from '@/contexts/ThemeContext';

const OrganizationSetup: React.FC = () => {
  const { theme } = useTheme();
  const [activeTab, setActiveTab] = useState('profile');

  // Define tabs with RBAC checks if necessary
  const tabs = [
    {
      id: 'profile',
      label: 'Company Profile',
      icon: Building,
    },
    {
      id: 'hierarchy',
      label: 'Org Chart',
      icon: Network,
    },
    {
      id: 'leadership',
      label: 'Leadership',
      icon: Users,
    },
    {
      id: 'plants',
      label: 'Locations',
      icon: Factory,
    },
    {
      id: 'departments',
      label: 'Departments',
      icon: Building,
    },
    {
      id: 'job-levels',
      label: 'Job Levels',
      icon: Briefcase,
    },
    {
      id: 'designations',
      label: 'Job Titles',
      icon: Users,
    },
  ];

  return (
    <DetailLayout
      aria-label="Organization Setup"
      className="animate-in fade-in duration-500"
      containerClassName="max-w-[1600px]"
      header={<div className="h-6" />}
      tabs={
        <div className="max-w-[1600px] mx-auto px-6 pb-0">
          <HorizontalTabs
            tabs={tabs}
            activeTabId={activeTab}
            onTabChange={setActiveTab}
            className="mb-0"
            wrap
          />
        </div>
      }
    >
      <div className="min-h-[500px]">
        {activeTab === 'profile' && <OrgProfile />}
        {activeTab === 'hierarchy' && <HierarchyChart />}
        {activeTab === 'leadership' && <LeadershipManagement />}
        {activeTab === 'plants' && <PlantManagement />}
        {activeTab === 'departments' && <DepartmentManagement onSync={() => {}} />}
        {activeTab === 'designations' && <DesignationManagement onSync={() => {}} />}
        {activeTab === 'job-levels' && <JobLevelManagement onSync={() => {}} />}
      </div>
    </DetailLayout>
  );
};

const OrganizationSetupWithBoundary: React.FC = () => (
  <ErrorBoundary>
    <OrganizationSetup />
  </ErrorBoundary>
);

export default OrganizationSetupWithBoundary;
