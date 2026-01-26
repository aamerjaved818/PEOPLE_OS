import React from 'react';
import { AuditDashboard } from './AuditDashboard';
import ErrorBoundary from '@/components/ErrorBoundary';

const SystemAuditModule: React.FC = () => (
  <ErrorBoundary>
    <div className="h-full w-full overflow-y-auto overscroll-contain custom-scrollbar px-6 md:px-10 pb-10">
      <div className="w-full pb-20">
        <AuditDashboard />
      </div>
    </div>
  </ErrorBoundary>
);

export default SystemAuditModule;
