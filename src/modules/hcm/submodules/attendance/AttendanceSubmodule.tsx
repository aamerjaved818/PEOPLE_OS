import React, { useState } from 'react';
import { HorizontalTabs } from '@/components/ui/HorizontalTabs';
import ShiftManagement from './ShiftManagement';

// Hooks
import { useAttendance } from './hooks/useAttendance';
import { useAttendanceCorrections } from './hooks/useAttendanceCorrections';

// Components
import { AttendanceHeader } from './components/AttendanceHeader';
import { AttendanceStats } from './components/AttendanceStats';
import { DailyLog } from './components/DailyLog';
import { AttendanceMatrix } from './components/AttendanceMatrix';
import { CorrectionRequests } from './components/CorrectionRequests';
import { CompliancePanel } from './components/CompliancePanel';

type AttendanceTab = 'daily' | 'matrix' | 'corrections' | 'shifts';

const Attendance: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AttendanceTab>('daily');
  const [currentMonth] = useState('July 2024');

  const {
    searchTerm,
    setSearchTerm,
    attendanceRecords,
    filteredRecords,
    isLoading,
    plants,
    selectedPlantId,
    loadData,
  } = useAttendance();

  const { correctionRequests, handleCorrectionAction, pendingCount } = useAttendanceCorrections();

  return (
    <div className="space-y-12 animate-in fade-in duration-700 pb-20">
      {/* Header Section */}
      <AttendanceHeader selectedPlantId={selectedPlantId} plants={plants} onRefresh={loadData} />

      {/* Stats Section */}
      <AttendanceStats />

      {/* Navigation Tabs */}
      <HorizontalTabs
        tabs={[
          { id: 'daily', label: 'Daily Log' },
          { id: 'matrix', label: 'Attendance Matrix' },
          { id: 'corrections', label: 'Corrections' },
          { id: 'shifts', label: 'Shift Management' },
        ]}
        activeTabId={activeTab}
        onTabChange={(id) => setActiveTab(id as AttendanceTab)}
        wrap={true}
        disabled={isLoading}
      />

      {/* Content Area */}
      <main>
        {activeTab === 'daily' && (
          <DailyLog
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            filteredRecords={filteredRecords}
            isLoading={isLoading}
          />
        )}

        {activeTab === 'matrix' && (
          <AttendanceMatrix currentMonth={currentMonth} attendanceRecords={attendanceRecords} />
        )}

        {activeTab === 'corrections' && (
          <CorrectionRequests
            requests={correctionRequests}
            onAction={handleCorrectionAction}
            pendingCount={pendingCount}
          />
        )}

        {activeTab === 'shifts' && <ShiftManagement onSync={loadData} />}
      </main>

      {/* Footer Compliance Section */}
      <CompliancePanel />
    </div>
  );
};

export default Attendance;
