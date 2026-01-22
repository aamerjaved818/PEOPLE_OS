import React from 'react';
import { Save } from 'lucide-react';
import EmployeeDetailHeader from './EmployeeDetailHeader';
import EmployeeTabs from './EmployeeTabs';
import EmployeeInfoTab from './EmployeeInfoTab';
import PayrollTab from './PayrollTab';
import FamilyTab from './FamilyTab';
import EducationTab from './EducationTab';
import ExperienceTab from './ExperienceTab';

import DisciplineTab from './DisciplineTab';
import { DetailLayout } from '../../components/layout/DetailLayout';
import { Button } from '../../components/ui/Button';
import { Employee as EmployeeType } from '../../types';

interface EmployeeMasterProps {
  currentEmployee: Partial<EmployeeType> | null;
  activeTab: number;
  setActiveTab: (tab: number) => void;
  updateField: (field: keyof EmployeeType, value: any) => void;
  isAnalyzing: boolean;
  aiSuggestions: any[];
  isDisabled?: boolean;
  isNewRecord?: boolean;
  onSave: () => void;
  onBack: () => void;
  onExit?: (emp: EmployeeType) => void;
}

const EmployeeMaster: React.FC<EmployeeMasterProps> = ({
  currentEmployee,
  activeTab,
  setActiveTab,
  updateField,
  isAnalyzing,
  aiSuggestions,
  isDisabled,
  isNewRecord = false,
  onSave,
  onBack,
  onExit,
}) => {
  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return (
          <EmployeeInfoTab
            employee={currentEmployee}
            updateField={updateField}
            isAnalyzing={isAnalyzing}
            aiSuggestions={aiSuggestions}
            onExit={onExit}
            isNewRecord={isNewRecord}
          />
        );
      case 1:
        return (
          <PayrollTab
            employee={currentEmployee}
            updateField={updateField}
            isNewRecord={isNewRecord}
          />
        );
      case 2:
        return <FamilyTab employee={currentEmployee} updateField={updateField} />;
      case 3:
        return <EducationTab employee={currentEmployee} updateField={updateField} />;
      case 4:
        return <ExperienceTab employee={currentEmployee} updateField={updateField} />;
      case 5:
        return <DisciplineTab employee={currentEmployee} updateField={updateField} />;
      default:
        return null;
    }
  };

  return (
    <DetailLayout
      aria-label="Employee Details"
      header={<EmployeeDetailHeader employee={currentEmployee} aiSuggestions={aiSuggestions} />}
      tabs={
        <div className="flex flex-col">
          <EmployeeTabs activeTab={activeTab} onTabChange={setActiveTab} disabled={isDisabled} />
          <div className="px-8 lg:px-12 pb-6">
            <div className="max-w-7xl mx-auto flex gap-4 p-4 bg-surface rounded-lg shadow-md border border-border">
              <button
                onClick={onBack}
                disabled={isDisabled}
                className="px-10 py-4 text-text-secondary font-black uppercase text-[0.6875rem] tracking-widest hover:bg-muted-bg rounded-md transition-all disabled:opacity-50"
              >
                Back
              </button>
              <Button
                onClick={onSave}
                isLoading={isDisabled}
                icon={Save}
                className="px-14 py-4 bg-primary text-white hover:bg-primary-hover"
              >
                {isDisabled ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </div>
      }
    >
      {renderTabContent()}
    </DetailLayout>
  );
};

export default EmployeeMaster;
