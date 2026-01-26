import React, { useState, useEffect } from 'react';
import { Plus, Pause, Play, Trash2, Zap, Edit2, Calendar } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { API_CONFIG } from '@/config/constants';

interface Schedule {
  id: string;
  report_name: string;
  report_type: string;
  format: string;
  frequency: string;
  recipients: string[];
  is_active: boolean;
  next_run: string;
  last_run: string | null;
  created_at: string;
}

interface ScheduleManagerProps {
  onScheduleCreated?: () => void;
}

const ScheduleManager: React.FC<ScheduleManagerProps> = ({ onScheduleCreated }) => {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState<Schedule | null>(null);
  const [triggering, setTriggering] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    report_name: '',
    report_type: 'sales',
    format: 'pdf',
    frequency: 'weekly',
    recipients: '',
    include_summary: true,
  });

  useEffect(() => {
    fetchSchedules();
  }, []);

  const fetchSchedules = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_CONFIG.BASE_URL}/analytics/schedules`);
      if (!response.ok) {
        throw new Error('Failed to fetch schedules');
      }
      const data = await response.json();
      setSchedules(data);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const recipients = formData.recipients
      .split(',')
      .map((email) => email.trim())
      .filter((email) => email);

    if (recipients.length === 0) {
      setError('At least one recipient is required');
      return;
    }

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/analytics/schedules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          recipients,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create schedule');
      }

      setFormData({
        report_name: '',
        report_type: 'sales',
        format: 'pdf',
        frequency: 'weekly',
        recipients: '',
        include_summary: true,
      });
      setShowForm(false);
      await fetchSchedules();
      onScheduleCreated?.();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handlePause = async (scheduleId: string) => {
    try {
      const response = await fetch(
        `${API_CONFIG.BASE_URL}/analytics/schedules/${scheduleId}/pause`,
        {
          method: 'POST',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to pause schedule');
      }
      await fetchSchedules();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handleResume = async (scheduleId: string) => {
    try {
      const response = await fetch(
        `${API_CONFIG.BASE_URL}/analytics/schedules/${scheduleId}/resume`,
        {
          method: 'POST',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to resume schedule');
      }
      await fetchSchedules();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handleDelete = async (scheduleId: string) => {
    if (!confirm('Are you sure you want to delete this schedule?')) {
      return;
    }

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/analytics/schedules/${scheduleId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete schedule');
      }
      await fetchSchedules();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handleTrigger = async (scheduleId: string) => {
    try {
      setTriggering(scheduleId);
      const response = await fetch(
        `${API_CONFIG.BASE_URL}/analytics/schedules/${scheduleId}/trigger`,
        {
          method: 'POST',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to trigger report');
      }
      const data = await response.json();
      alert(`Report generation started. Task ID: ${data.task_id}`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setTriggering(null);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-10 bg-gray-200 rounded w-1/4"></div>
          <div className="h-6 bg-gray-200 rounded"></div>
          <div className="h-6 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Report Schedules</h1>
            <p className="text-gray-600 mt-2">Manage recurring report delivery</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            <Plus size={20} />
            New Schedule
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-sm text-red-600 hover:underline mt-2"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Create Form */}
        {showForm && (
          <div className="mb-8 bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Create New Schedule</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Report Name
                  </label>
                  <input
                    type="text"
                    value={formData.report_name}
                    onChange={(e) => setFormData({ ...formData, report_name: e.target.value })}
                    placeholder="e.g., Weekly Sales Report"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Report Type
                  </label>
                  <select
                    value={formData.report_type}
                    onChange={(e) => setFormData({ ...formData, report_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="sales">Sales</option>
                    <option value="recruitment">Recruitment</option>
                    <option value="performance">Performance</option>
                    <option value="headcount">Headcount</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Format</label>
                  <select
                    value={formData.format}
                    onChange={(e) => setFormData({ ...formData, format: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="pdf">PDF</option>
                    <option value="excel">Excel</option>
                    <option value="html">HTML</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
                  <select
                    value={formData.frequency}
                    onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="biweekly">Bi-weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Recipients (comma-separated emails)
                  </label>
                  <input
                    type="text"
                    value={formData.recipients}
                    onChange={(e) => setFormData({ ...formData, recipients: e.target.value })}
                    placeholder="email1@example.com, email2@example.com"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="col-span-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.include_summary}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          include_summary: e.target.checked,
                        })
                      }
                      className="rounded"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Include metrics summary in email
                    </span>
                  </label>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  Create Schedule
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Schedules List */}
        {schedules.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Calendar size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No schedules yet</h3>
            <p className="text-gray-600 mb-6">Create your first schedule to start receiving</p>
            <button
              onClick={() => setShowForm(true)}
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              <Plus size={20} />
              Create Schedule
            </button>
          </div>
        ) : (
          <div className="grid gap-6">
            {schedules.map((schedule) => (
              <div key={schedule.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{schedule.report_name}</h3>
                    <p className="text-sm text-gray-600">
                      {schedule.report_type.charAt(0).toUpperCase() + schedule.report_type.slice(1)}{' '}
                      • {schedule.format.toUpperCase()}
                    </p>
                  </div>
                  <div
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      schedule.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {schedule.is_active ? 'Active' : 'Paused'}
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-4 mb-6 text-sm">
                  <div>
                    <p className="text-gray-600">Frequency</p>
                    <p className="font-medium text-gray-900 capitalize">{schedule.frequency}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Recipients</p>
                    <p className="font-medium text-gray-900">{schedule.recipients.length}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Last Run</p>
                    <p className="font-medium text-gray-900">
                      {schedule.last_run
                        ? formatDistanceToNow(new Date(schedule.last_run), {
                            addSuffix: true,
                          })
                        : 'Never'}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Next Run</p>
                    <p className="font-medium text-gray-900">
                      {formatDistanceToNow(new Date(schedule.next_run), {
                        addSuffix: true,
                      })}
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => handleTrigger(schedule.id)}
                    disabled={triggering === schedule.id}
                    className="flex items-center gap-2 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition disabled:opacity-50"
                  >
                    <Zap size={16} />
                    Trigger Now
                  </button>

                  {schedule.is_active ? (
                    <button
                      onClick={() => handlePause(schedule.id)}
                      className="flex items-center gap-2 px-3 py-2 bg-yellow-50 text-yellow-600 rounded-lg hover:bg-yellow-100 transition"
                    >
                      <Pause size={16} />
                      Pause
                    </button>
                  ) : (
                    <button
                      onClick={() => handleResume(schedule.id)}
                      className="flex items-center gap-2 px-3 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition"
                    >
                      <Play size={16} />
                      Resume
                    </button>
                  )}

                  <button
                    onClick={() => setSelectedSchedule(schedule)}
                    className="flex items-center gap-2 px-3 py-2 bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition"
                  >
                    <Edit2 size={16} />
                    Edit
                  </button>

                  <button
                    onClick={() => handleDelete(schedule.id)}
                    className="flex items-center gap-2 px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition ml-auto"
                  >
                    <Trash2 size={16} />
                    Delete
                  </button>
                </div>

                {schedule.recipients.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-xs text-gray-600 mb-2">Recipients:</p>
                    <div className="flex flex-wrap gap-2">
                      {schedule.recipients.map((email) => (
                        <span
                          key={email}
                          className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                        >
                          {email}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ScheduleManager;
