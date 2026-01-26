import React, { useEffect, useState, useRef, useCallback } from 'react';
import { api } from '@/services/api';
import { useTheme } from '@/contexts/ThemeContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loader2, RefreshCw, Terminal, Download, Power, AlertCircle } from 'lucide-react';

const LogViewer: React.FC = () => {
  const { theme } = useTheme();
  void theme;
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  // Auto-start log streaming on app load
  const [autoStarted, setAutoStarted] = useState(false);
  const retryRef = useRef<{ attempt: number; timeoutId: number | null }>({
    attempt: 0,
    timeoutId: null,
  });

  const fetchLogsRef = useRef<(() => Promise<void>) | null>(null);

  const scheduleRetry = useCallback(() => {
    const maxAttempts = 6;
    const attempt = Math.min(retryRef.current.attempt, maxAttempts);
    const delay = Math.min(60000, 500 * Math.pow(2, attempt)); // ms
    retryRef.current.attempt = attempt + 1;

    if (retryRef.current.timeoutId) {
      clearTimeout(retryRef.current.timeoutId as any);
    }
    // @ts-ignore - NodeJS/Browser timer typing
    retryRef.current.timeoutId = window.setTimeout(() => {
      fetchLogsRef.current?.();
    }, delay) as any;
  }, []);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getSystemLogs(200);
      setLogs(data.logs || []);
      // successful fetch -> reset retry attempts
      if (retryRef.current.timeoutId) {
        clearTimeout(retryRef.current.timeoutId as any);
        retryRef.current.timeoutId = null;
      }
      retryRef.current.attempt = 0;
    } catch (err) {
      // Provide more detailed error for debugging and user action
      const message = err instanceof Error ? err.message : String(err);
      setError(`Failed to load system logs: ${message}`);
      // schedule retry with exponential backoff
      scheduleRetry();
    } finally {
      setLoading(false);
    }
  }, [scheduleRetry]);

  useEffect(() => {
    fetchLogsRef.current = fetchLogs;
  }, [fetchLogs]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  useEffect(() => {
    let interval: number | undefined;

    // capture current retryRef for cleanup stability
    const currentRetry = retryRef.current;

    // Start auto-refresh automatically on first mount (system start behavior)
    if (!autoStarted) {
      setAutoStarted(true);
      setAutoRefresh(true);
    }

    if (autoRefresh) {
      // initial fetch immediately
      fetchLogs();
      // periodic poll
      // @ts-ignore
      interval = window.setInterval(fetchLogs, 5000);
    }

    return () => {
      if (interval) {
        clearInterval(interval as any);
      }
      if (currentRetry && currentRetry.timeoutId) {
        clearTimeout(currentRetry.timeoutId as any);
        currentRetry.timeoutId = null;
      }
    };
  }, [autoRefresh, fetchLogs, autoStarted]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const downloadLogs = () => {
    const blob = new Blob([logs.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `people_os_logs_${new Date().toISOString()}.log`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const getLogColor = (line: string) => {
    if (line.includes('ERROR') || line.includes('CRITICAL')) {
      return 'text-red-400 font-bold';
    }
    if (line.includes('WARNING')) {
      return 'text-yellow-400';
    }
    if (line.includes('INFO')) {
      return 'text-blue-300';
    }
    return 'text-green-300'; // Debug/Default
  };

  return (
    <Card className="h-full border-zinc-800 bg-zinc-950 shadow-2xl flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b border-zinc-800 shrink-0">
        <div className="space-y-1">
          <CardTitle className="text-xl font-mono flex items-center gap-2 text-zinc-100">
            <Terminal className="h-5 w-5 text-purple-500" />
            System Kernel Logs
          </CardTitle>
          <CardDescription className="text-zinc-500">
            Real-time feed from people_os.log
          </CardDescription>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={autoRefresh ? 'secondary' : 'outline'}
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={
              autoRefresh
                ? 'bg-green-900/20 text-green-400 border-green-900'
                : 'border-zinc-700 text-zinc-400'
            }
          >
            <Power className={`h-4 w-4 mr-2 ${autoRefresh ? 'text-green-500' : 'text-zinc-500'}`} />
            {autoRefresh ? 'Live' : 'Paused'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchLogs}
            disabled={loading && !autoRefresh}
            className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={downloadLogs}
            className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0 flex-1 overflow-hidden relative">
        <div
          className="h-[600px] bg-black font-mono text-sm p-4 overflow-auto scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-zinc-900"
          ref={scrollRef}
        >
          {error ? (
            <div className="mb-4 bg-red-950/70 border border-red-600 text-red-100 p-4 rounded-lg flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-300 mt-1 flex-shrink-0" />
              <div className="flex-1">
                <div className="font-bold text-red-200">Connection Error</div>
                <div className="max-w-xl mt-1 text-red-100 leading-snug">{error}</div>
                <div className="mt-3 flex items-center gap-3">
                  <Button
                    onClick={fetchLogs}
                    className="px-3 py-1 text-sm rounded-md bg-red-600 text-white hover:bg-red-500 border border-red-700 h-auto"
                  >
                    Retry
                  </Button>
                  <Button
                    onClick={() => {
                      console.error('System logs error:', error);
                      try {
                        alert('Error details printed to console.');
                      } catch (e) {
                        console.warn('Alert popup failed', e);
                      }
                    }}
                    variant="outline"
                    className="ml-1 px-3 py-1 text-sm rounded-md bg-zinc-900/40 text-red-100 hover:bg-zinc-900/30 border border-red-700 h-auto"
                  >
                    Details
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-1 pb-4">
              {logs.length === 0 && !loading && (
                <div className="text-zinc-600 text-center mt-20">-- No logs found --</div>
              )}
              {logs.map((line, i) => (
                <div key={i} className={`whitespace-pre-wrap break-all ${getLogColor(line)}`}>
                  <span className="opacity-50 mr-4 select-none text-zinc-600">
                    {(i + 1).toString().padStart(4, '0')}
                  </span>
                  {line}
                </div>
              ))}
              {loading && !autoRefresh && (
                <div className="flex items-center justify-center p-4 text-zinc-500">
                  <Loader2 className="h-4 w-4 animate-spin mr-2" /> Fetching latest bytes...
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default LogViewer;
