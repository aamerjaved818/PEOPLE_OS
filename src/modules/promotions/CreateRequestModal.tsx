import React, { useState, useEffect } from 'react';
import { X, FileText, DollarSign, TrendingUp } from 'lucide-react';
import api from '@/services/api';
import { PromotionRequest, Employee, Designation, Grade, PromotionCycle } from '@/types';

interface CreateRequestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (request: PromotionRequest) => void;
  cycles: PromotionCycle[];
}

const CreateRequestModal: React.FC<CreateRequestModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  cycles,
}) => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [grades, setGrades] = useState<Grade[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  // Form State
  const [formData, setFormData] = useState({
    employeeId: '',
    cycleId: '',
    type: 'Both' as 'Increment' | 'Promotion' | 'Both',
    effectiveDate: '',
    currentSalary: 0,
    proposedSalary: 0,
    currentDesignationId: '',
    proposedDesignationId: '',
    proposedGradeId: '',
    reason: '',
  });

  useEffect(() => {
    if (isOpen) {
      fetchData();
    }
  }, [isOpen]);

  const fetchData = async () => {
    try {
      setInitialLoading(true);
      const [empData, desData, gradeData] = await Promise.all([
        api.getEmployees(),
        api.getDesignations(),
        api.getGrades(),
      ]);
      setEmployees(empData);
      setDesignations(desData);
      setGrades(gradeData);
    } catch (error) {
      console.error('Failed to load form data', error);
    } finally {
      setInitialLoading(false);
    }
  };

  const handleEmployeeChange = (empId: string) => {
    const emp = employees.find((e) => e.id === empId);
    if (emp) {
      setFormData((prev) => ({
        ...prev,
        employeeId: empId,
        currentSalary: emp.grossSalary || 0,
        proposedSalary: emp.grossSalary || 0, // Default to current
        currentDesignationId: emp.designation_id || '',
        proposedDesignationId: emp.designation_id || '', // Default to current
      }));
    } else {
      setFormData((prev) => ({ ...prev, employeeId: empId }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload: any = {
        ...formData,
        cycleId: formData.cycleId ? parseInt(formData.cycleId) : undefined,
        currentSalary: Number(formData.currentSalary),
        proposedSalary: Number(formData.proposedSalary),
        status: 'Pending',
        organizationId: 'current-org-id', // Backend handles this usually
      };

      const newRequest = await api.savePromotionRequest(payload);
      onSuccess(newRequest);
      onClose();
    } catch (error) {
      console.error('Failed to create request', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-[2rem] w-full max-w-2xl shadow-2xl p-8 max-h-[90vh] overflow-y-auto custom-scrollbar relative animate-in zoom-in-95 duration-200">
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-2 bg-slate-50 rounded-full hover:bg-slate-100 transition-colors z-10"
        >
          <X className="w-5 h-5 text-slate-500" />
        </button>

        <div className="space-y-2 mb-8">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center">
              <FileText className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-2xl font-black text-slate-800 tracking-tight">New Proposal</h2>
              <p className="text-slate-500">
                Submit an increment or promotion request for approval.
              </p>
            </div>
          </div>
        </div>

        {initialLoading ? (
          <div className="py-20 flex justify-center">
            <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Employee Selection */}
              <div className="space-y-1 md:col-span-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1">
                  Employee
                </label>
                <select
                  required
                  className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-xl font-bold text-slate-700 focus:outline-none focus:border-indigo-500 transition-all"
                  value={formData.employeeId}
                  onChange={(e) => handleEmployeeChange(e.target.value)}
                >
                  <option value="">Select Employee</option>
                  {employees.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.name} ({emp.designation})
                    </option>
                  ))}
                </select>
              </div>

              {/* Cycle & Type */}
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1">
                  Review Cycle
                </label>
                <select
                  className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-xl font-bold text-slate-700 focus:outline-none focus:border-indigo-500 transition-all"
                  value={formData.cycleId}
                  onChange={(e) => setFormData({ ...formData, cycleId: e.target.value })}
                >
                  <option value="">No Specific Cycle (Ad-hoc)</option>
                  {cycles
                    .filter((c) => c.status === 'Open')
                    .map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.title}
                      </option>
                    ))}
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1">
                  Proposal Type
                </label>
                <select
                  required
                  className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-xl font-bold text-slate-700 focus:outline-none focus:border-indigo-500 transition-all"
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                >
                  <option value="Increment">Increment Only</option>
                  <option value="Promotion">Promotion Only</option>
                  <option value="Both">Both (Increment & Promotion)</option>
                </select>
              </div>

              {/* Financials */}
              <div className="md:col-span-2 space-y-4 p-5 bg-slate-50 rounded-2xl border border-slate-100">
                <h4 className="flex items-center gap-2 font-black text-slate-800 text-sm uppercase tracking-wide">
                  <DollarSign className="w-4 h-4 text-emerald-500" /> Financial Details
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-widest pl-1">
                      Current Salary
                    </label>
                    <input
                      type="number"
                      disabled
                      className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl font-bold text-slate-500 cursor-not-allowed"
                      value={formData.currentSalary}
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-indigo-500 uppercase tracking-widest pl-1">
                      Proposed Salary
                    </label>
                    <input
                      type="number"
                      required
                      className="w-full px-4 py-3 bg-white border-2 border-indigo-100 rounded-xl font-bold text-indigo-700 focus:outline-none focus:border-indigo-500 transition-all"
                      value={formData.proposedSalary}
                      onChange={(e) =>
                        setFormData({ ...formData, proposedSalary: Number(e.target.value) })
                      }
                    />
                  </div>
                </div>
              </div>

              {/* Role Change (Conditional) */}
              {(formData.type === 'Promotion' || formData.type === 'Both') && (
                <div className="md:col-span-2 space-y-4 p-5 bg-slate-50 rounded-2xl border border-slate-100">
                  <h4 className="flex items-center gap-2 font-black text-slate-800 text-sm uppercase tracking-wide">
                    <TrendingUp className="w-4 h-4 text-purple-500" /> Role Change
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <label className="text-xs font-bold text-slate-400 uppercase tracking-widest pl-1">
                        Current Role
                      </label>
                      <select
                        disabled
                        className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl font-bold text-slate-500 cursor-not-allowed"
                        value={formData.currentDesignationId}
                      >
                        <option value="">
                          {formData.currentDesignationId
                            ? designations.find((d) => d.id === formData.currentDesignationId)?.name
                            : 'N/A'}
                        </option>
                      </select>
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-bold text-purple-500 uppercase tracking-widest pl-1">
                        New Role
                      </label>
                      <select
                        required={formData.type !== ('Increment' as any)}
                        className="w-full px-4 py-3 bg-white border-2 border-purple-100 rounded-xl font-bold text-slate-700 focus:outline-none focus:border-purple-500 transition-all"
                        value={formData.proposedDesignationId}
                        onChange={(e) =>
                          setFormData({ ...formData, proposedDesignationId: e.target.value })
                        }
                      >
                        <option value="">Select New Designation</option>
                        {designations.map((d) => (
                          <option key={d.id} value={d.id}>
                            {d.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-1 md:col-span-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1">
                  Effective Date
                </label>
                <input
                  type="date"
                  required
                  className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-xl font-bold text-slate-700 focus:outline-none focus:border-indigo-500 transition-all"
                  value={formData.effectiveDate}
                  onChange={(e) => setFormData({ ...formData, effectiveDate: e.target.value })}
                />
              </div>

              <div className="space-y-1 md:col-span-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest pl-1">
                  Justification / Remarks
                </label>
                <textarea
                  rows={3}
                  className="w-full px-4 py-3 bg-slate-50 border-2 border-slate-100 rounded-xl font-medium text-slate-700 focus:outline-none focus:border-indigo-500 transition-all resize-none"
                  placeholder="Why is this promotion/increment being recommended?"
                  value={formData.reason}
                  onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
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
                    Submitting...
                  </>
                ) : (
                  'Submit Proposal'
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default CreateRequestModal;
