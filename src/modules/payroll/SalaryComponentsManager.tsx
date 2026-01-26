/**
 * SalaryComponentsManager - Configure salary components
 * Manage earnings and deductions for the organization
 */

import React, { useState, useEffect } from 'react';
import {
  Plus,
  Edit2,
  Trash2,
  RefreshCw,
  DollarSign,
  Percent,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { payrollApi, SalaryComponent } from '@/services/payrollApi';
import { formatCurrency } from '@/utils/formatting';

const SalaryComponentsManager: React.FC = () => {
  const [components, setComponents] = useState<SalaryComponent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingComponent, setEditingComponent] = useState<SalaryComponent | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [form, setForm] = useState({
    code: '',
    name: '',
    description: '',
    componentType: 'earning' as 'earning' | 'deduction',
    calculationType: 'fixed' as 'fixed' | 'percentage',
    percentageOf: '',
    defaultAmount: 0,
    isTaxable: true,
    isStatutory: false,
    displayOrder: 0,
  });

  useEffect(() => {
    loadComponents();
  }, []);

  const loadComponents = async () => {
    try {
      setLoading(true);
      const response = await payrollApi.getSalaryComponents(false);
      setComponents(response.data || []);
    } catch (error) {
      console.error('Failed to load components:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      if (editingComponent) {
        await payrollApi.updateSalaryComponent(editingComponent.id, form);
      } else {
        await payrollApi.createSalaryComponent(form as any);
      }
      setShowModal(false);
      resetForm();
      loadComponents();
    } catch (error) {
      console.error('Failed to save component:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (component: SalaryComponent) => {
    setEditingComponent(component);
    setForm({
      code: component.code,
      name: component.name,
      description: component.description || '',
      componentType: component.componentType,
      calculationType: component.calculationType,
      percentageOf: component.percentageOf || '',
      defaultAmount: component.defaultAmount,
      isTaxable: component.isTaxable,
      isStatutory: component.isStatutory,
      displayOrder: component.displayOrder,
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to deactivate this component?')) {
      return;
    }
    try {
      await payrollApi.deleteSalaryComponent(id);
      loadComponents();
    } catch (error) {
      console.error('Failed to delete component:', error);
    }
  };

  const resetForm = () => {
    setEditingComponent(null);
    setForm({
      code: '',
      name: '',
      description: '',
      componentType: 'earning',
      calculationType: 'fixed',
      percentageOf: '',
      defaultAmount: 0,
      isTaxable: true,
      isStatutory: false,
      displayOrder: 0,
    });
  };

  const earnings = components.filter((c) => c.componentType === 'earning');
  const deductions = components.filter((c) => c.componentType === 'deduction');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-text-primary tracking-tight">
            Salary Components
          </h1>
          <p className="text-sm text-text-muted mt-1">Configure earnings and deductions</p>
        </div>
        <button
          onClick={() => {
            resetForm();
            setShowModal(true);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg font-bold hover:bg-primary/90 transition-all shadow-lg"
        >
          <Plus className="w-4 h-4" />
          Add Component
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-surface rounded-xl border border-border p-4">
          <p className="text-xs font-bold text-text-muted uppercase">Total Components</p>
          <p className="text-2xl font-black text-text-primary mt-1">{components.length}</p>
        </div>
        <div className="bg-success/10 rounded-xl border border-success/20 p-4">
          <p className="text-xs font-bold text-success uppercase">Earnings</p>
          <p className="text-2xl font-black text-success mt-1">{earnings.length}</p>
        </div>
        <div className="bg-danger/10 rounded-xl border border-danger/20 p-4">
          <p className="text-xs font-bold text-danger uppercase">Deductions</p>
          <p className="text-2xl font-black text-danger mt-1">{deductions.length}</p>
        </div>
      </div>

      {/* Components Table */}
      <div className="bg-surface rounded-xl border border-border shadow-md overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted">
            <tr className="text-xs font-black uppercase text-text-muted tracking-wider">
              <th className="px-6 py-4 text-left">Code</th>
              <th className="px-6 py-4 text-left">Name</th>
              <th className="px-6 py-4 text-center">Type</th>
              <th className="px-6 py-4 text-center">Calculation</th>
              <th className="px-6 py-4 text-center">Taxable</th>
              <th className="px-6 py-4 text-center">Status</th>
              <th className="px-6 py-4 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-text-muted">
                  <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2" />
                  Loading...
                </td>
              </tr>
            ) : components.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-text-muted">
                  No components yet. Add your first component!
                </td>
              </tr>
            ) : (
              components.map((c) => (
                <tr key={c.id} className="hover:bg-muted/30 transition-colors">
                  <td className="px-6 py-4">
                    <span className="font-mono font-bold text-primary">{c.code}</span>
                  </td>
                  <td className="px-6 py-4">
                    <p className="font-bold text-text-primary">{c.name}</p>
                    {c.description && <p className="text-xs text-text-muted">{c.description}</p>}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold ${
                        c.componentType === 'earning'
                          ? 'bg-success/20 text-success'
                          : 'bg-danger/20 text-danger'
                      }`}
                    >
                      {c.componentType === 'earning' ? (
                        <DollarSign className="w-3 h-3" />
                      ) : (
                        <Percent className="w-3 h-3" />
                      )}
                      {c.componentType}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className="text-xs font-bold text-text-muted uppercase">
                      {c.calculationType}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    {c.isTaxable ? (
                      <CheckCircle className="w-4 h-4 text-success mx-auto" />
                    ) : (
                      <XCircle className="w-4 h-4 text-text-muted mx-auto" />
                    )}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span
                      className={`text-xs font-bold ${c.isActive ? 'text-success' : 'text-text-muted'}`}
                    >
                      {c.isActive ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        onClick={() => handleEdit(c)}
                        className="p-1.5 bg-muted text-text-muted hover:text-primary rounded-lg transition-colors"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(c.id)}
                        className="p-1.5 bg-muted text-text-muted hover:text-danger rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-surface rounded-xl border border-border shadow-2xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-black text-text-primary mb-4">
              {editingComponent ? 'Edit Component' : 'Add Component'}
            </h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-text-muted mb-1">Code</label>
                  <input
                    type="text"
                    value={form.code}
                    onChange={(e) => setForm({ ...form, code: e.target.value })}
                    placeholder="e.g., HRA"
                    className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-text-muted mb-1">Name</label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    placeholder="e.g., House Rent Allowance"
                    className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-text-muted mb-1">Type</label>
                  <select
                    value={form.componentType}
                    onChange={(e) => setForm({ ...form, componentType: e.target.value as any })}
                    className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
                  >
                    <option value="earning">Earning</option>
                    <option value="deduction">Deduction</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-text-muted mb-1">
                    Calculation
                  </label>
                  <select
                    value={form.calculationType}
                    onChange={(e) => setForm({ ...form, calculationType: e.target.value as any })}
                    className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
                  >
                    <option value="fixed">Fixed Amount</option>
                    <option value="percentage">Percentage</option>
                  </select>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.isTaxable}
                    onChange={(e) => setForm({ ...form, isTaxable: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-bold text-text-muted">Taxable</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.isStatutory}
                    onChange={(e) => setForm({ ...form, isStatutory: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <span className="text-sm font-bold text-text-muted">Statutory</span>
                </label>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => {
                  setShowModal(false);
                  resetForm();
                }}
                className="px-4 py-2 bg-muted text-text-muted rounded-lg font-bold hover:bg-muted/80"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={!form.code || !form.name || submitting}
                className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg font-bold hover:bg-primary/90 disabled:opacity-50"
              >
                {submitting ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Plus className="w-4 h-4" />
                )}
                {editingComponent ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalaryComponentsManager;
