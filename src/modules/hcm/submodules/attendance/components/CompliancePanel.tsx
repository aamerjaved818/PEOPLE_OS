import React from 'react';
import { ShieldCheck } from 'lucide-react';

export const CompliancePanel: React.FC = () => {
  return (
    <div className="bg-surface p-20 rounded-md text-text-primary shadow-md relative overflow-hidden group border border-border">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-transparent to-transparent pointer-events-none"></div>
      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center gap-20">
        <div className="w-32 h-32 bg-primary text-white rounded-md flex items-center justify-center shadow-md animate-pulse shrink-0">
          <ShieldCheck className="w-16 h-16" />
        </div>
        <div className="flex-1">
          <h3 className="text-4xl font-black tracking-tighter antialiased leading-none">
            Compliance Audit
          </h3>
          <p className="text-text-muted mt-8 text-xl max-w-4xl leading-relaxed antialiased">
            Every timestamp is securely logged. Discrepancies trigger automatic alerts, ensuring
            100% legal compliance.
          </p>
        </div>
        <button
          aria-label="View full audit logs"
          className="px-16 py-6 bg-primary text-surface rounded-md font-black uppercase text-[0.75rem] tracking-[0.3em] hover:scale-105 active:scale-95 transition-all shadow-md shrink-0"
        >
          View Logs
        </button>
      </div>
    </div>
  );
};
