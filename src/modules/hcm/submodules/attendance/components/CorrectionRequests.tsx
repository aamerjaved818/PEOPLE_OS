import React from 'react';
import { Check, X } from 'lucide-react';
import { VibrantBadge } from '@/components/ui/VibrantBadge';

interface CorrectionRequest {
  id: string;
  name: string;
  date: string;
  type: string;
  reason: string;
  status: string;
}

interface CorrectionRequestsProps {
  requests: CorrectionRequest[];
  onAction: (id: string, action: 'Approved' | 'Rejected') => void;
  pendingCount: number;
}

export const CorrectionRequests: React.FC<CorrectionRequestsProps> = ({
  requests,
  onAction,
  pendingCount,
}) => {
  return (
    <div className="space-y-10 animate-in slide-in-from-left-8 duration-700">
      <div className="bg-surface rounded-md border border-border shadow-md overflow-hidden min-h-[31.25rem]">
        <div className="p-12 border-b border-border bg-muted-bg/30 backdrop-blur-3xl flex items-center justify-between">
          <div>
            <h3 className="text-3xl font-black text-text-primary tracking-tight">
              Manual Corrections
            </h3>
            <p className="text-[0.625rem] font-black text-text-muted uppercase tracking-widest mt-2">
              Attendance Correction Requests
            </p>
          </div>
          <span className="px-6 py-2 bg-danger-soft text-danger rounded-full text-[0.625rem] font-black uppercase tracking-widest border border-danger/20">
            {pendingCount} Pending Approvals
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-muted-bg/50 text-[0.6875rem] font-black uppercase text-text-muted tracking-[0.25em]">
                <th className="px-14 py-8">Employee</th>
                <th className="px-8 py-8">Date</th>
                <th className="px-8 py-8">Type</th>
                <th className="px-8 py-8">Reason</th>
                <th className="px-14 py-8 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {requests.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-14 py-8 text-center text-text-muted">
                    No pending corrections.
                  </td>
                </tr>
              ) : (
                requests.map((req, i) => (
                  <tr key={i} className="group hover:bg-danger-soft/20 transition-all">
                    <td className="px-14 py-8">
                      <p className="text-lg font-black text-text-primary">{req.name}</p>
                      <p className="text-[0.625rem] font-black text-text-muted uppercase tracking-widest mt-2">
                        LHR-NODE-99
                      </p>
                    </td>
                    <td className="px-8 py-8 text-sm font-bold text-text-muted uppercase">
                      {req.date}
                    </td>
                    <td className="px-8 py-8">
                      <span className="text-xs font-black text-primary uppercase tracking-tighter">
                        {req.type}
                      </span>
                    </td>
                    <td className="px-8 py-8 max-w-xs text-xs font-medium text-text-muted leading-relaxed italic">
                      "{req.reason}"
                    </td>
                    <td className="px-14 py-8 text-right">
                      {req.status === 'Pending' ? (
                        <div className="flex justify-end gap-3 opacity-0 group-hover:opacity-100 transition-all">
                          <button
                            onClick={() => onAction(req.id, 'Approved')}
                            aria-label="Approve request"
                            className="p-4 bg-success text-white rounded-md shadow-md hover:scale-110 active:scale-90 transition-all"
                          >
                            <Check size={18} />
                          </button>
                          <button
                            onClick={() => onAction(req.id, 'Rejected')}
                            aria-label="Reject request"
                            className="p-4 bg-danger text-white rounded-md shadow-md hover:scale-110 active:scale-90 transition-all"
                          >
                            <X size={18} />
                          </button>
                        </div>
                      ) : (
                        <VibrantBadge color={req.status === 'Approved' ? 'green' : 'pink'}>
                          {req.status}
                        </VibrantBadge>
                      )}
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
