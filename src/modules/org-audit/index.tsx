import React from 'react';
import { SystemLogViewer } from '../system-audit/components/SystemLogViewer';
import ErrorBoundary from '@/components/ErrorBoundary';

const OrgAuditModule: React.FC = () => (
  <ErrorBoundary>
    <div className="h-full w-full overflow-y-auto overscroll-contain custom-scrollbar px-6 md:px-10 pb-10">
      <div className="w-full pb-20">
        <div className="mb-8">
          <h2 className="text-3xl font-black text-text-primary uppercase tracking-tight flex items-center gap-3">
            Organization Audit
            <span className="text-xs px-2 py-1 bg-primary/20 text-primary rounded-md font-black tracking-widest uppercase">
              Org Scoped
            </span>
          </h2>
          <p className="text-sm text-text-muted mt-1">
            Audit trail for all organizational data changes
          </p>
        </div>
        <SystemLogViewer />
      </div>
    </div>
  </ErrorBoundary>
);

export default OrgAuditModule;
