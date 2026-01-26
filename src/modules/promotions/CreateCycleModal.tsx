import React, { useState } from 'react';
import { X, Calendar } from 'lucide-react';
import api from '@/services/api';
import { PromotionCycle } from '@/types';

interface CreateCycleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (cycle: PromotionCycle) => void;
}

const CreateCycleModal: React.FC<CreateCycleModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    startDate: '',
    endDate: '',
  });
  const [loading, setLoading] = useState(false);

  if (!isOpen) {return null;}

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const newCycle = await api.savePromotionCycle({
        ...formData,
        status: 'Open',
        organizationId: 'current-org-id', // Handled by backend context
      } as any);
      onSuccess(newCycle);
      onClose();
    } catch (error) {
      console.error('Failed to create cycle', error);
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
            <Calendar className="w-6 h-6 text-indigo-600" />
          </div>
          <h2 className="text-2xl font-black text-slate-800 tracking-tight">New Review Cycle</h2>
          <p className="text-slate-500">
            Initialize a new employee performance review and increment cycle.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1">
              Cycle Title
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Annual Review 2025"
              className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-xl font-bold text-slate-700 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all placeholder:font-medium placeholder:text-slate-400"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1">
                Start Date
              </label>
              <input
                type="date"
                required
                className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-xl font-bold text-slate-700 focus:outline-none focus:border-indigo-500 transition-all"
                value={formData.startDate}
                onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1">
                End Date
              </label>
              <input
                type="date"
                className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-xl font-bold text-slate-700 focus:outline-none focus:border-indigo-500 transition-all"
                value={formData.endDate}
                onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
              />
            </div>
          </div>

          <div className="pt-4 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3.5 rounded-xl font-bold text-slate-500 hover:text-slate-700 hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-[2] py-3.5 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-200 disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Creating...
                </>
              ) : (
                'Launch Cycle'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateCycleModal;
