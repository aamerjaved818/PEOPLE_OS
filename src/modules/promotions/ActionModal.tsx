import React, { useState } from 'react';
import { X, ShieldCheck, XCircle, CheckCircle } from 'lucide-react';
import api from '@/services/api';
import { PromotionRequest } from '@/types';

interface ActionModalProps {
  isOpen: boolean;
  onClose: () => void;
  request: PromotionRequest | null;
  onSuccess: (updatedRequest: PromotionRequest) => void;
}

const ActionModal: React.FC<ActionModalProps> = ({ isOpen, onClose, request, onSuccess }) => {
  const [remarks, setRemarks] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen || !request) {return null;}

  const determineNextLevel = (currentStatus: string) => {
    switch (currentStatus) {
      case 'Pending':
        return 'HR';
      case 'HR_Approved':
        return 'Finance';
      case 'Finance_Approved':
        return 'Final';
      default:
        return 'Final';
    }
  };

  const nextLevel = determineNextLevel(request.status);

  const handleAction = async (status: 'Approved' | 'Rejected') => {
    setLoading(true);
    try {
      const updated = await api.approvePromotionRequest({
        requestId: request.id,
        level: nextLevel,
        status: status,
        remarks: remarks,
      });
      onSuccess(updated);
      onClose();
    } catch (error) {
      console.error('Failed to process request', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-[2rem] w-full max-w-md shadow-2xl p-8 space-y-6 relative animate-in zoom-in-95 duration-200">
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-2 bg-slate-50 rounded-full hover:bg-slate-100 transition-colors"
        >
          <X className="w-5 h-5 text-slate-500" />
        </button>

        <div className="space-y-2">
          <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center">
            <ShieldCheck className="w-6 h-6 text-indigo-600" />
          </div>
          <h2 className="text-2xl font-black text-slate-800 tracking-tight">Review Proposal</h2>
          <p className="text-slate-500">
            Action required for <strong>{request.employee?.name}</strong> as{' '}
            <strong>{nextLevel}</strong> Approver.
          </p>
        </div>

        <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-slate-500 font-bold">Current Status</span>
            <span className="font-bold text-slate-700">{request.status}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-500 font-bold">Request Type</span>
            <span className="font-bold text-slate-700">{request.type}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-500 font-bold">Proposed Salary</span>
            <span className="font-bold text-indigo-600">
              ${request.proposedSalary.toLocaleString()}
            </span>
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1">
            Remarks
          </label>
          <textarea
            rows={3}
            className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-xl font-medium text-slate-700 focus:outline-none focus:border-indigo-500 transition-all resize-none"
            placeholder="Add any comments regarding this decision..."
            value={remarks}
            onChange={(e) => setRemarks(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-2 gap-3 pt-2">
          <button
            onClick={() => handleAction('Rejected')}
            disabled={loading}
            className="flex items-center justify-center gap-2 py-3.5 bg-white border-2 border-rose-100 text-rose-600 rounded-xl font-bold hover:bg-rose-50 hover:border-rose-200 transition-all disabled:opacity-70"
          >
            <XCircle className="w-5 h-5" />
            Reject
          </button>
          <button
            onClick={() => handleAction('Approved')}
            disabled={loading}
            className="flex items-center justify-center gap-2 py-3.5 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-200 disabled:opacity-70"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            ) : (
              <>
                <CheckCircle className="w-5 h-5" />
                Approve as {nextLevel}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ActionModal;
