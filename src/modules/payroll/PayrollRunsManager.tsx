/**
 * PayrollRunsManager - Manage payroll processing batches
 * Create, process, and finalize monthly payroll runs
 */

import React, { useState, useEffect } from 'react';
import {
  Play,
  CheckCircle,
  Clock,
  Plus,
  RefreshCw,
  DollarSign,
  Calendar,
  FileText,
} from 'lucide-react';
import { payrollApi, PayrollRun } from '@/services/payrollApi';
import { formatCurrency } from '@/utils/formatting';

const MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

const PayrollRunsManager: React.FC = () => {
  const [runs, setRuns] = useState<PayrollRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedRun, setSelectedRun] = useState<PayrollRun | null>(null);
  const [processing, setProcessing] = useState(false);

  // New run form
  const [newMonth, setNewMonth] = useState(MONTHS[new Date().getMonth()]);
  const [newYear, setNewYear] = useState(new Date().getFullYear().toString());

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      setLoading(true);
      const response = await payrollApi.getPayrollRuns();
      setRuns(response.data || []);
    } catch (error) {
      console.error('Failed to load payroll runs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRun = async () => {
    try {
      setProcessing(true);
      await payrollApi.createPayrollRun({
        periodMonth: newMonth,
        periodYear: newYear,
      });
      setShowCreateModal(false);
      loadRuns();
    } catch (error) {
      console.error('Failed to create payroll run:', error);
    } finally {
      setProcessing(false);
    }
  };

  const handleProcess = async (runId: string) => {
    try {
      setProcessing(true);
      await payrollApi.processPayrollRun(runId);
      loadRuns();
    } catch (error) {
      console.error('Failed to process payroll:', error);
    } finally {
      setProcessing(false);
    }
  };

  const handleFinalize = async (runId: string) => {
    try {
      setProcessing(true);
      await payrollApi.finalizePayrollRun(runId);
      loadRuns();
    } catch (error) {
      console.error('Failed to finalize payroll:', error);
    } finally {
      setProcessing(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Draft':
        return <Clock className="w-4 h-4" />;
      case 'Processing':
        return <RefreshCw className="w-4 h-4 animate-spin" />;
      case 'Processed':
        return <CheckCircle className="w-4 h-4" />;
      case 'Paid':
        return <DollarSign className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Draft':
        return 'bg-muted text-text-muted';
      case 'Processing':
        return 'bg-warning/20 text-warning';
      case 'Processed':
        return 'bg-primary/20 text-primary';
      case 'Paid':
        return 'bg-success/20 text-success';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-text-primary tracking-tight">Payroll Runs</h1>
          <p className="text-sm text-text-muted mt-1">Manage monthly payroll processing</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg font-bold hover:bg-primary/90 transition-all shadow-lg"
        >
          <Plus className="w-4 h-4" />
          New Payroll Run
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Runs', value: runs.length, icon: Calendar, color: 'primary' },
          {
            label: 'Draft',
            value: runs.filter((r) => r.status === 'Draft').length,
            icon: Clock,
            color: 'muted',
          },
          {
            label: 'Processed',
            value: runs.filter((r) => r.status === 'Processed').length,
            icon: CheckCircle,
            color: 'warning',
          },
          {
            label: 'Paid',
            value: runs.filter((r) => r.status === 'Paid').length,
            icon: DollarSign,
            color: 'success',
          },
        ].map((stat, i) => (
          <div key={i} className="bg-surface rounded-xl border border-border p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-text-muted uppercase tracking-wider">
                  {stat.label}
                </p>
                <p className="text-2xl font-black text-text-primary mt-1">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-lg bg-${stat.color}/10`}>
                <stat.icon className={`w-5 h-5 text-${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Runs Table */}
      <div className="bg-surface rounded-xl border border-border shadow-md overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted">
            <tr className="text-xs font-black uppercase text-text-muted tracking-wider">
              <th className="px-6 py-4 text-left">Period</th>
              <th className="px-6 py-4 text-left">Status</th>
              <th className="px-6 py-4 text-right">Employees</th>
              <th className="px-6 py-4 text-right">Gross</th>
              <th className="px-6 py-4 text-right">Net</th>
              <th className="px-6 py-4 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-text-muted">
                  <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2" />
                  Loading...
                </td>
              </tr>
            ) : runs.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-text-muted">
                  No payroll runs yet. Create your first one!
                </td>
              </tr>
            ) : (
              runs.map((run) => (
                <tr key={run.id} className="hover:bg-muted/30 transition-colors">
                  <td className="px-6 py-4">
                    <p className="font-bold text-text-primary">
                      {run.periodMonth} {run.periodYear}
                    </p>
                    <p className="text-xs text-text-muted mt-0.5">{run.id}</p>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${getStatusColor(run.status)}`}
                    >
                      {getStatusIcon(run.status)}
                      {run.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className="font-mono font-bold text-text-primary">
                      {run.totalEmployees}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className="font-mono font-bold text-text-primary">
                      {formatCurrency(run.totalGross)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className="font-mono font-bold text-success">
                      {formatCurrency(run.totalNet)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-center gap-2">
                      {run.status === 'Draft' && (
                        <button
                          onClick={() => handleProcess(run.id)}
                          disabled={processing}
                          className="flex items-center gap-1 px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-bold hover:bg-primary/90 disabled:opacity-50"
                        >
                          <Play className="w-3 h-3" />
                          Process
                        </button>
                      )}
                      {run.status === 'Processed' && (
                        <button
                          onClick={() => handleFinalize(run.id)}
                          disabled={processing}
                          className="flex items-center gap-1 px-3 py-1.5 bg-success text-white rounded-lg text-xs font-bold hover:bg-success/90 disabled:opacity-50"
                        >
                          <CheckCircle className="w-3 h-3" />
                          Finalize
                        </button>
                      )}
                      <button
                        onClick={() => setSelectedRun(run)}
                        className="p-1.5 bg-muted text-text-muted hover:text-primary rounded-lg transition-colors"
                        title="View Details"
                      >
                        <FileText className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-surface rounded-xl border border-border shadow-2xl w-full max-w-md p-6">
            <h2 className="text-xl font-black text-text-primary mb-4">Create Payroll Run</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-text-muted mb-1">Month</label>
                <select
                  value={newMonth}
                  onChange={(e) => setNewMonth(e.target.value)}
                  className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
                >
                  {MONTHS.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-bold text-text-muted mb-1">Year</label>
                <input
                  type="text"
                  value={newYear}
                  onChange={(e) => setNewYear(e.target.value)}
                  className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-text-primary font-medium"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-muted text-text-muted rounded-lg font-bold hover:bg-muted/80"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateRun}
                disabled={processing}
                className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg font-bold hover:bg-primary/90 disabled:opacity-50"
              >
                {processing ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Plus className="w-4 h-4" />
                )}
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PayrollRunsManager;
