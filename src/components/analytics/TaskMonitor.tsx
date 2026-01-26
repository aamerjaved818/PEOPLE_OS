import React, { useState, useEffect, useCallback } from 'react';
import { CheckCircle, AlertCircle, Clock, RefreshCw, Trash2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Task {
  task_id: string;
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | 'RETRY' | 'PROGRESS';
  result?: {
    schedule_id: string;
    file_path: string;
    recipients: string[];
    generated_at: string;
    message: string;
  };
  error?: string;
  created_at?: string;
}

interface TaskMonitorProps {
  refreshInterval?: number; // milliseconds
  maxTasks?: number;
}

const TaskMonitor: React.FC<TaskMonitorProps> = ({ refreshInterval = 5000, maxTasks = 10 }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      // Get tasks from localStorage (simulated task tracking)
      const storedTasks = localStorage.getItem('reportTasks');
      if (storedTasks) {
        const parsedTasks = JSON.parse(storedTasks).slice(0, maxTasks);
        setTasks(parsedTasks);
      }
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [maxTasks]);

  // Polling for task status
  useEffect(() => {
    const interval = setInterval(fetchTasks, refreshInterval);
    fetchTasks(); // Initial fetch
    return () => clearInterval(interval);
  }, [refreshInterval, fetchTasks]);

  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'SUCCESS':
        return <CheckCircle className="text-green-600" size={20} />;
      case 'FAILURE':
        return <AlertCircle className="text-red-600" size={20} />;
      case 'PROGRESS':
      case 'STARTED':
        return <RefreshCw className="text-blue-600 animate-spin" size={20} />;
      default:
        return <Clock className="text-yellow-600" size={20} />;
    }
  };

  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'SUCCESS':
        return 'bg-green-50 border-green-200';
      case 'FAILURE':
        return 'bg-red-50 border-red-200';
      case 'PROGRESS':
      case 'STARTED':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-yellow-50 border-yellow-200';
    }
  };

  const getStatusBadge = (status: Task['status']) => {
    switch (status) {
      case 'SUCCESS':
        return 'bg-green-100 text-green-800';
      case 'FAILURE':
        return 'bg-red-100 text-red-800';
      case 'PROGRESS':
      case 'STARTED':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const removeTask = (taskId: string) => {
    const storedTasks = localStorage.getItem('reportTasks');
    if (storedTasks) {
      const filtered = JSON.parse(storedTasks).filter((t: Task) => t.task_id !== taskId);
      localStorage.setItem('reportTasks', JSON.stringify(filtered));
      setTasks(filtered);
    }
  };

  const clearCompleted = () => {
    const storedTasks = localStorage.getItem('reportTasks');
    if (storedTasks) {
      const filtered = JSON.parse(storedTasks).filter(
        (t: Task) => t.status !== 'SUCCESS' && t.status !== 'FAILURE'
      );
      localStorage.setItem('reportTasks', JSON.stringify(filtered));
      setTasks(filtered);
    }
  };

  if (loading && tasks.length === 0) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/4"></div>
          <div className="h-12 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 rounded-lg">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Report Tasks</h2>
          <p className="text-gray-600 text-sm mt-1">
            {tasks.length} task{tasks.length !== 1 ? 's' : ''} in queue
          </p>
        </div>

        {tasks.some((t) => t.status === 'SUCCESS' || t.status === 'FAILURE') && (
          <button
            onClick={clearCompleted}
            className="text-sm px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition"
          >
            Clear Completed
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {tasks.length === 0 ? (
        <div className="text-center py-12">
          <Clock className="mx-auto text-gray-400 mb-3" size={32} />
          <p className="text-gray-600">No tasks yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => (
            <div
              key={task.task_id}
              className={`border rounded-lg p-4 ${getStatusColor(task.status)}`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1">
                  {getStatusIcon(task.status)}

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className={`text-xs font-semibold px-2 py-1 rounded ${getStatusBadge(
                          task.status
                        )}`}
                      >
                        {task.status}
                      </span>
                    </div>

                    <p className="text-sm font-medium text-gray-900 break-all">
                      Task ID: {task.task_id}
                    </p>

                    {task.result && (
                      <div className="mt-3 space-y-2 text-sm">
                        <div>
                          <p className="text-gray-600">Report:</p>
                          <p className="text-gray-900">
                            {task.result.file_path?.split('/').pop() || 'Generated'}
                          </p>
                        </div>

                        {task.result.recipients && task.result.recipients.length > 0 && (
                          <div>
                            <p className="text-gray-600">Recipients:</p>
                            <div className="flex flex-wrap gap-1">
                              {task.result.recipients.map((email) => (
                                <span
                                  key={email}
                                  className="px-2 py-1 bg-white bg-opacity-50 rounded text-xs"
                                >
                                  {email}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {task.result.generated_at && (
                          <div>
                            <p className="text-gray-600">Generated:</p>
                            <p className="text-gray-900">
                              {formatDistanceToNow(new Date(task.result.generated_at), {
                                addSuffix: true,
                              })}
                            </p>
                          </div>
                        )}

                        {task.result.message && (
                          <div>
                            <p className="text-gray-600">Message:</p>
                            <p className="text-gray-900">{task.result.message}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {task.error && (
                      <div className="mt-3 p-2 bg-white bg-opacity-50 rounded text-sm text-red-700">
                        {task.error}
                      </div>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => removeTask(task.task_id)}
                  className="text-gray-400 hover:text-gray-600 transition flex-shrink-0"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Status Legend */}
      <div className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
        <div className="flex items-center gap-2">
          <Clock className="text-yellow-600" size={16} />
          <span className="text-gray-600">Pending</span>
        </div>
        <div className="flex items-center gap-2">
          <RefreshCw className="text-blue-600" size={16} />
          <span className="text-gray-600">Processing</span>
        </div>
        <div className="flex items-center gap-2">
          <CheckCircle className="text-green-600" size={16} />
          <span className="text-gray-600">Success</span>
        </div>
        <div className="flex items-center gap-2">
          <AlertCircle className="text-red-600" size={16} />
          <span className="text-gray-600">Failed</span>
        </div>
      </div>
    </div>
  );
};

export default TaskMonitor;
