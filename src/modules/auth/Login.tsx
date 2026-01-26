import React, { useState } from 'react';
import { Lock, User, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { sanitizeInput } from '@/utils/security';
import { api } from '@/services/api';
import GlassCard from '@/components/ui/GlassCard';
import { useTheme } from '@/contexts/ThemeContext';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

interface LoginProps {
  onLogin: () => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const { theme } = useTheme();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const safeUsername = sanitizeInput(username);
    // Raw password should be sent for backend verification
    const safePassword = password;

    try {
      const loginSuccess = await api.login(safeUsername, safePassword, false);

      if (loginSuccess) {
        setSuccess(true);
        // Quick success animation then proceed
        setTimeout(() => {
          onLogin();
        }, 200);
      } else {
        setError('Invalid credentials');
        setLoading(false);
      }
    } catch (err: any) {
      // Differentiate between network errors and others
      const isNetworkError =
        !err.response && (err.name === 'TypeError' || err.message?.includes('fetch'));
      if (isNetworkError) {
        const targetUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
        setError(`Cannot reach server at ${targetUrl}. Please check if the backend is running.`);
      } else {
        setError(err.message || 'Login failed. Please check your credentials.');
      }
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen w-full flex items-center justify-center p-4 relative overflow-hidden"
      role="main"
    >
      {/* Background Effects */}
      <div className="absolute inset-0 bg-app z-0"></div>
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
        <div className="absolute top-[10%] left-[20%] w-96 h-96 bg-primary/20 rounded-full blur-[100px] animate-pulse-slow"></div>
        <div className="absolute bottom-[10%] right-[20%] w-96 h-96 bg-purple-500/10 rounded-full blur-[100px] animate-pulse-slow delay-1000"></div>
      </div>

      <GlassCard
        className={`relative z-10 max-w-md w-full p-8 md:p-10 animate-in zoom-in-95 fade-in duration-500`}
      >
        <div className="text-center mb-10">
          <div className="group relative w-20 h-20 mx-auto mb-6">
            <div className="absolute inset-0 bg-primary/20 rounded-2xl rotate-6 group-hover:rotate-12 transition-transform duration-300"></div>
            <div className="absolute inset-0 bg-primary rounded-2xl flex items-center justify-center shadow-lg shadow-primary/30 group-hover:scale-105 transition-transform duration-300">
              <Lock className="text-white w-10 h-10" strokeWidth={2.5} />
            </div>
          </div>
          <h1 className="text-3xl font-black text-text-primary uppercase tracking-tight mb-2">
            Welcome Back
          </h1>
          <p className="text-text-muted font-medium">
            Enter your credentials to access{' '}
            <span className="text-primary font-bold">People OS</span>
          </p>
          {theme === 'dark' && (
            <p className="text-[10px] text-primary/50 mt-2 font-black uppercase tracking-[0.2em]">
              Dark Protocol Active
            </p>
          )}
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-start gap-3 text-red-600 animate-in slide-in-from-top-2">
            <AlertCircle size={20} className="shrink-0 mt-0.5" />
            <span className="text-sm font-bold">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6" aria-label="Login Credentials">
          <div className="space-y-2 group">
            <Input
              label="Username"
              icon={User}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="sysadmin"
              aria-label="Username"
              disabled={loading || success}
              autoFocus
            />
          </div>

          <div className="space-y-2 group">
            <div className="flex justify-between items-center ml-1 mb-1">
              <label className="text-[0.625rem] font-black text-text-muted uppercase tracking-widest">
                Security
              </label>
              <a
                href="#"
                className="text-[0.625rem] font-black text-primary hover:text-primary-hover hover:underline uppercase tracking-widest"
              >
                Forgot?
              </a>
            </div>
            <Input
              type="password"
              icon={Lock}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              aria-label="Password"
              disabled={loading || success}
            />
          </div>

          <Button
            type="submit"
            isLoading={loading}
            size="lg"
            className={`w-full ${success ? 'bg-green-500 shadow-green-500/25 scale-[1.02]' : ''}`}
          >
            {success ? (
              <div className="flex items-center gap-2">
                <CheckCircle2 size={20} className="animate-in zoom-in spin-in-90" />
                <span>Access Granted</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <span>Sign In Dashboard</span>
                <ArrowRight size={20} />
              </div>
            )}
          </Button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-xs text-text-muted font-medium">
            Protected by <span className="text-primary font-bold">PeopleOS Security™</span>
          </p>
        </div>
      </GlassCard>
    </div>
  );
};

export default Login;
