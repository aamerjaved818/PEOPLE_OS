/**
 * TaxDeductionsPortal - Employee tax deduction claims
 * Submit tuition fees, donations, and other tax-deductible expenses
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  GraduationCap,
  Heart,
  Shield,
  Plus,
  Trash2,
  CheckCircle,
  Clock,
  XCircle,
  RefreshCw,
  Calculator,
  FileText,
} from 'lucide-react';
import {
  payrollApi,
  TaxDeductionType,
  EmployeeTaxDeduction,
  TaxCalculationDetail,
} from '@/services/payrollApi';
import { formatCurrency } from '@/utils/formatting';

interface TaxDeductionsPortalProps {
  employeeId: string;
  taxYear?: string;
}

const TaxDeductionsPortal: React.FC<TaxDeductionsPortalProps> = ({
  employeeId,
  taxYear = '2025-2026',
}) => {
  const [deductionTypes, setDeductionTypes] = useState<TaxDeductionType[]>([]);
  const [myDeductions, setMyDeductions] = useState<EmployeeTaxDeduction[]>([]);
  const [taxCalculation, setTaxCalculation] = useState<TaxCalculationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // New deduction form
  const [selectedType, setSelectedType] = useState('');
  const [claimedAmount, setClaimedAmount] = useState('');
  const [numChildren, setNumChildren] = useState('');
  const [institutionName, setInstitutionName] = useState('');
  const [institutionNtn, setInstitutionNtn] = useState('');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [typesRes, deductionsRes, calcRes] = await Promise.all([
        payrollApi.getTaxDeductionTypes(),
        payrollApi.getEmployeeTaxDeductions(employeeId, taxYear),
        payrollApi.getTaxCalculation(employeeId, taxYear),
      ]);
      setDeductionTypes(typesRes.data || []);
      setMyDeductions(deductionsRes.data || []);
      setTaxCalculation(calcRes.data || null);
    } catch (error) {
      console.error('Failed to load tax data:', error);
    } finally {
      setLoading(false);
    }
  }, [employeeId, taxYear]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      await payrollApi.createEmployeeTaxDeduction(employeeId, {
        deductionTypeId: selectedType,
        taxYear,
        claimedAmount: parseFloat(claimedAmount),
        numberOfChildren: numChildren ? parseInt(numChildren) : undefined,
        institutionName: institutionName || undefined,
        institutionNtn: institutionNtn || undefined,
      });
      setShowAddModal(false);
      resetForm();
      loadData();
    } catch (error) {
      console.error('Failed to submit deduction:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (deductionId: number) => {
    if (!confirm('Are you sure you want to delete this claim?')) {
      return;
    }
    try {
      await payrollApi.deleteEmployeeTaxDeduction(employeeId, deductionId);
      loadData();
    } catch (error) {
      console.error('Failed to delete deduction:', error);
    }
  };

  const resetForm = () => {
    setSelectedType('');
    setClaimedAmount('');
    setNumChildren('');
    setInstitutionName('');
    setInstitutionNtn('');
  };

  const getSectionIcon = (section: string) => {
    switch (section) {
      case '60D':
        return <GraduationCap className="w-5 h-5 text-primary" />;
      case '62':
        return <Heart className="w-5 h-5 text-danger" />;
      case '63':
        return <Shield className="w-5 h-5 text-success" />;
      case '64':
        return <Shield className="w-5 h-5 text-warning" />;
      default:
        return <FileText className="w-5 h-5 text-text-muted" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Pending':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-warning/20 text-warning rounded-full text-xs font-bold">
            <Clock className="w-3 h-3" /> Pending
          </span>
        );
      case 'Approved':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-success/20 text-success rounded-full text-xs font-bold">
            <CheckCircle className="w-3 h-3" /> Approved
          </span>
        );
      case 'Rejected':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-danger/20 text-danger rounded-full text-xs font-bold">
            <XCircle className="w-3 h-3" /> Rejected
          </span>
        );
      default:
        return null;
    }
  };

  const selectedDeductionType = deductionTypes.find((t) => t.id === selectedType);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-text-primary tracking-tight">Tax Deductions</h1>
          <p className="text-sm text-text-muted mt-1">
            Tax Year {taxYear} - Income Tax Ordinance 2001
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg font-bold hover:bg-primary/90 transition-all shadow-lg"
        >
          <Plus className="w-4 h-4" />
          Add Claim
        </button>
      </div>

      {/* Tax Calculation Summary */}
      {taxCalculation && (
        <div className="bg-gradient-to-br from-primary/10 to-success/10 rounded-xl border border-primary/20 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Calculator className="w-5 h-5 text-primary" />
            <h2 className="font-black text-text-primary">Tax Calculation Summary</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-text-muted uppercase tracking-wider">Annual Income</p>
              <p className="text-lg font-black text-text-primary">
                {formatCurrency(taxCalculation.annualGrossIncome)}
              </p>
            </div>
            <div>
              <p className="text-xs text-text-muted uppercase tracking-wider">Deductions</p>
              <p className="text-lg font-black text-success">
                -{formatCurrency(taxCalculation.totalDeductibleAllowances)}
              </p>
            </div>
            <div>
              <p className="text-xs text-text-muted uppercase tracking-wider">Taxable Income</p>
              <p className="text-lg font-black text-text-primary">
                {formatCurrency(taxCalculation.taxableIncome)}
              </p>
            </div>
            <div>
              <p className="text-xs text-text-muted uppercase tracking-wider">Monthly Tax</p>
              <p className="text-lg font-black text-danger">
                {formatCurrency(taxCalculation.monthlyTax)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* My Deductions */}
      <div className="bg-surface rounded-xl border border-border shadow-md overflow-hidden">
        <div className="p-4 border-b border-border bg-muted/30">
          <h3 className="font-black text-text-primary uppercase tracking-wider text-sm">
            My Claims
          </h3>
        </div>
        <div className="divide-y divide-border">
          {loading ? (
            <div className="p-8 text-center text-text-muted">
              <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2" />
              Loading...
            </div>
          ) : myDeductions.length === 0 ? (
            <div className="p-8 text-center text-text-muted">
              No tax deduction claims yet. Add your first claim!
            </div>
          ) : (
            myDeductions.map((deduction) => (
              <div
                key={deduction.id}
                className="p-4 flex items-center justify-between hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-center gap-4">
                  {getSectionIcon(deduction.deductionSection || '')}
                  <div>
                    <p className="font-bold text-text-primary">{deduction.deductionTypeName}</p>
                    <p className="text-xs text-text-muted">
                      Section {deduction.deductionSection}
                      {deduction.institutionName && ` • ${deduction.institutionName}`}
                      {deduction.numberOfChildren && ` • ${deduction.numberOfChildren} children`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="font-mono font-bold text-text-primary">
                      {formatCurrency(deduction.claimedAmount)}
                    </p>
                    {getStatusBadge(deduction.status)}
                  </div>
                  {deduction.status === 'Pending' && (
                    <button
                      onClick={() => handleDelete(deduction.id)}
                      className="p-2 text-text-muted hover:text-danger rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Available Deduction Types */}
      <div className="bg-surface rounded-xl border border-border shadow-md p-6">
        <h3 className="font-black text-text-primary uppercase tracking-wider text-sm mb-4">
          Available Deductions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {deductionTypes.map((type) => (
            <div key={type.id} className="p-4 bg-muted/30 rounded-lg border border-border">
              <div className="flex items-center gap-3 mb-2">
                {getSectionIcon(type.section)}
                <div>
                  <p className="font-bold text-text-primary">{type.name}</p>
                  <p className="text-xs text-primary font-bold">Section {type.section}</p>
                </div>
              </div>
              <p className="text-xs text-text-muted">{type.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-surface rounded-xl border border-border shadow-2xl w-full max-w-lg p-6">
            <h2 className="text-xl font-black text-text-primary mb-4">Add Tax Deduction Claim</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-text-muted mb-1">
                  Deduction Type
                </label>
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
                >
                  <option value="">Select type...</option>
                  {deductionTypes.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name} (Section {t.section})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-bold text-text-muted mb-1">Amount (PKR)</label>
                <input
                  type="number"
                  value={claimedAmount}
                  onChange={(e) => setClaimedAmount(e.target.value)}
                  placeholder="e.g., 400000"
                  className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
                />
              </div>
              {selectedDeductionType?.section === '60D' && (
                <div>
                  <label className="block text-sm font-bold text-text-muted mb-1">
                    Number of Children
                  </label>
                  <input
                    type="number"
                    value={numChildren}
                    onChange={(e) => setNumChildren(e.target.value)}
                    placeholder="e.g., 2"
                    className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
                  />
                </div>
              )}
              {selectedDeductionType?.requiresNtn && (
                <>
                  <div>
                    <label className="block text-sm font-bold text-text-muted mb-1">
                      Institution Name
                    </label>
                    <input
                      type="text"
                      value={institutionName}
                      onChange={(e) => setInstitutionName(e.target.value)}
                      placeholder="e.g., Beacon House School"
                      className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-text-muted mb-1">
                      Institution NTN
                    </label>
                    <input
                      type="text"
                      value={institutionNtn}
                      onChange={(e) => setInstitutionNtn(e.target.value)}
                      placeholder="e.g., 1234567-8"
                      className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
                    />
                  </div>
                </>
              )}
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => {
                  setShowAddModal(false);
                  resetForm();
                }}
                className="px-4 py-2 bg-muted text-text-muted rounded-lg font-bold hover:bg-muted/80"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={!selectedType || !claimedAmount || submitting}
                className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg font-bold hover:bg-primary/90 disabled:opacity-50"
              >
                {submitting ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Plus className="w-4 h-4" />
                )}
                Submit Claim
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaxDeductionsPortal;
