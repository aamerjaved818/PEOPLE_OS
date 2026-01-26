import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  ShieldCheck,
  TrendingUp,
  LayoutDashboard,
  Building,
  Settings,
  Users,
  LogOut,
  Wallet,
  Gift,
  Target,
  GraduationCap,
  BrainCircuit,
  Smartphone,
  HeartPulse,
  Sparkles,
  UserCircle,
  Shield,
  BarChart3,
  Zap,
  Menu,
  ShieldOff,
  AlertTriangle,
  Sun,
  Moon,
  History,
} from 'lucide-react';
import { useRBAC } from '@/contexts/RBACContext';
import { ToastProvider } from '../ui/Toast';
import { useUIStore } from '@/store/uiStore';
import { useOrgStore } from '@/store/orgStore';
import { useTheme } from '@/contexts/ThemeContext';
import { useLayout } from '@/contexts/LayoutContext';
import GlassCard from '../ui/GlassCard';
import ThemeSwitcher from '../ui/ThemeSwitcher';
import AppRoutes from '../../routes';

// Lazy Load Core Components
const AIInsightsPanel = React.lazy(() => import('../AIInsightsPanel'));

interface AuthenticatedAppProps {
  onLogout: () => void;
}

const AuthenticatedApp: React.FC<AuthenticatedAppProps> = ({ onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const { sidebar, metrics } = useLayout();
  const { hasPermission } = useRBAC();

  const [hasHydrated, setHasHydrated] = useState(false);
  const asideRef = useRef<HTMLElement | null>(null);
  const [computedSidebarWidth, setComputedSidebarWidth] = useState<number>(
    sidebar.isOpen ? metrics.sidebarWidth || 320 : 0
  );
  const widthMeasuredRef = useRef(false);

  useEffect(() => {
    setHasHydrated(true);
  }, []);

  useEffect(() => {
    let ro: ResizeObserver | null = null;
    const timeoutId: ReturnType<typeof setTimeout> | null = null;
    let frameId: number | null = null;

    function updateWidth(el?: HTMLElement | null) {
      const target = el ?? asideRef.current;
      if (target && sidebar.isOpen) {
        const w = Math.ceil(target.getBoundingClientRect().width);
        const newWidth = w || metrics.sidebarWidth || 320;
        setComputedSidebarWidth(newWidth);
        widthMeasuredRef.current = true;
      } else {
        setComputedSidebarWidth(0);
        widthMeasuredRef.current = true;
      }
    }

    frameId = requestAnimationFrame(() => {
      frameId = requestAnimationFrame(() => {
        const el = asideRef.current;
        updateWidth(el);
        try {
          ro = new ResizeObserver(() => updateWidth(el));
          if (el && ro) {
            ro.observe(el);
          }
        } catch {
          window.addEventListener('resize', () => updateWidth(el));
        }
        window.addEventListener('resize', () => updateWidth(el));
      });
    });

    return () => {
      if (frameId) {
        cancelAnimationFrame(frameId);
      }
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      if (ro) {
        try {
          ro.disconnect();
        } catch {}
      }
      window.removeEventListener('resize', () => updateWidth(null));
    };
  }, [sidebar.isOpen, metrics.sidebarWidth]);

  const { setSidebarOpen, colorTheme } = useUIStore();
  const { currentUser } = useOrgStore();

  const isProfileInactive =
    currentUser?.userType === 'OrgUser' && currentUser?.profileStatus === 'Inactive';

  const [isAIPanelOpen, setAIPanelOpen] = useState(false);

  // Configuration (Mock/Local)
  const [config, setConfig] = useState(() => {
    const saved = localStorage.getItem('PeopleOS_config');
    return saved
      ? JSON.parse(saved)
      : {
          brandingName: 'people OS',
          enabledModules: {
            dashboard: true,
            employees: true,
            'org-settings': true,
            recruitment: true,
            'job-postings': true,
            onboarding: true,
            offboarding: true,
            attendance: true,
            leaves: true,
            overtime: true,
            payroll: true,
            'tax-compliance': true,
            compensation: true,
            benefits: true,
            performance: true,
            learning: true,
            skills: true,
            succession: true,
            engagement: true,
            rewards: true,
            relations: true,
            'health-safety': true,
            expenses: true,
            assets: true,
            alumni: true,
            analytics: true,
            workflow: true,
            'system-settings': true,
            integration: true,
            'self-service': true,
            visitors: true,
            assistance: true,
            'system-health': true,
            hcm: true,
            'system-audit': true,
            'org-audit': true,
          },
        };
  });

  // Apply Color Theme
  useEffect(() => {
    document.body.classList.remove('theme-quartz', 'theme-cyber', 'theme-forest', 'theme-sunset');
    document.body.classList.add(`theme-${colorTheme}`);
  }, [colorTheme]);

  useEffect(() => {
    const handleConfigUpdate = () => {
      const saved = localStorage.getItem('PeopleOS_config');
      if (saved) {
        setConfig(JSON.parse(saved));
      }
    };
    window.addEventListener('PeopleOS_config_updated', handleConfigUpdate);
    return () => window.removeEventListener('PeopleOS_config_updated', handleConfigUpdate);
  }, []);

  const navGroups = React.useMemo(
    () => [
      {
        title: '',
        items: [
          { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
          { id: 'admin', label: 'General Administration', icon: Shield },
          { id: 'hcm', label: 'Human Capital Mgmt', icon: Users },
          { id: 'org-audit', label: 'Organization Audit', icon: History },
          { id: 'org-settings', label: 'Organization Setup', icon: Building },
          { id: 'system-audit', label: 'System Audit', icon: ShieldCheck },
          { id: 'system-settings', label: 'System Settings', icon: Settings },
        ],
      },
      {
        title: 'II. Financials & Rewards',
        items: [
          { id: 'benefits', label: 'Benefits', icon: Gift },
          { id: 'compensation', label: 'Compensation (C&B)', icon: TrendingUp },
          { id: 'expenses', label: 'Expense Mgmt', icon: Wallet },
          { id: 'payroll', label: 'Payroll', icon: Wallet },
          { id: 'tax-compliance', label: 'Tax & Compliance', icon: ShieldCheck },
        ],
      },
      {
        title: 'III. Talent & Development',
        items: [
          { id: 'promotions', label: 'Increments & Promotions', icon: TrendingUp },
          { id: 'learning', label: 'L&D (LMS)', icon: GraduationCap },
          { id: 'performance', label: 'Performance Mgmt', icon: Target },
          { id: 'skills', label: 'Skills & Competency', icon: BrainCircuit },
          { id: 'succession', label: 'Talent & Succession', icon: TrendingUp },
        ],
      },
      {
        title: 'IV. Employee Experience',
        items: [
          { id: 'alumni', label: 'Alumni Mgmt', icon: Users },
          { id: 'relations', label: 'Employee Relations', icon: UserCircle },
          { id: 'engagement', label: 'Engagement', icon: HeartPulse },
          { id: 'health-safety', label: 'Health & Safety', icon: Shield },
          { id: 'rewards', label: 'Recognition', icon: Sparkles },
          { id: 'self-service', label: 'Self Service', icon: Smartphone },
        ],
      },
      {
        title: 'V. Intelligence & Auto',
        items: [
          { id: 'analytics', label: 'HR Analytics & BI', icon: BarChart3 },
          { id: 'workflow', label: 'Workflow & Auto', icon: Zap },
        ],
      },
    ],
    []
  );

  const filteredNavGroups = React.useMemo(() => {
    return navGroups
      .map((group) => ({
        ...group,
        items: group.items.filter((item) => {
          if (item.id === 'system-settings') {
            return hasPermission('system_config');
          }
          if (item.id === 'org-settings') {
            return hasPermission('manage_master_data');
          }
          return true;
        }),
      }))
      .filter((group) => group.items.length > 0);
  }, [hasPermission, navGroups]);

  // Determine active module based on URL
  const getActiveModuleFromPath = () => {
    const path = location.pathname.split('/')[1];
    return path || 'dashboard';
  };
  const activeModule = getActiveModuleFromPath();

  if (isProfileInactive) {
    return (
      <div className="min-h-screen bg-app flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-surface rounded-2xl shadow-2xl border border-danger/20 p-10 text-center animate-in zoom-in-95 duration-300">
          <div className="w-20 h-20 bg-danger/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <ShieldOff className="text-danger w-10 h-10" />
          </div>
          <h1 className="text-3xl font-black text-text-primary uppercase tracking-tight mb-4">
            Access Revoked
          </h1>
          <p className="text-text-muted font-medium mb-8">
            Your organizational profile has been marked as{' '}
            <span className="text-danger font-bold">Inactive</span>. Please contact your System
            Administrator or HR Department to restore access.
          </p>
          <div className="p-4 bg-muted-bg rounded-xl border border-border mb-8 text-left">
            <div className="flex items-start gap-3">
              <AlertTriangle className="text-warning shrink-0 mt-0.5" size={18} />
              <div>
                <p className="text-xs font-bold text-text-primary uppercase tracking-widest mb-1">
                  Security Notice
                </p>
                <p className="text-[10px] text-text-muted leading-relaxed">
                  This account is currently restricted from accessing the hcm core. All active
                  sessions have been terminated.
                </p>
              </div>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="w-full py-4 bg-muted-bg hover:bg-border text-text-primary rounded-xl font-bold uppercase tracking-widest transition-all flex items-center justify-center gap-2"
          >
            <LogOut size={20} />
            Sign Out
          </button>
        </div>
      </div>
    );
  }

  const safeSidebarWidth = metrics?.sidebarWidth || 280;
  const currentSidebarMargin = sidebar.isOpen
    ? widthMeasuredRef.current
      ? Math.max(computedSidebarWidth, safeSidebarWidth)
      : safeSidebarWidth
    : 0;

  return (
    <ToastProvider>
      <div
        className={`flex h-screen w-full transition-colors duration-500 bg-app overflow-hidden overscroll-none`}
      >
        <aside
          ref={asideRef}
          className={
            `fixed h-screen left-0 top-0 transform transition-transform duration-300 bg-surface flex flex-col z-50 shadow-2xl border-r border-blue-500/20 overflow-y-auto overscroll-contain custom-scrollbar min-w-[280px] w-auto ` +
            (sidebar.isOpen
              ? 'translate-x-0 opacity-100 pointer-events-auto'
              : '-translate-x-full opacity-0 pointer-events-none')
          }
        >
          <div className="flex flex-col items-center justify-center mb-3 mt-5 px-6 shrink-0">
            <div className="flex items-center gap-6 mb-2">
              <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-600/30 overflow-hidden shrink-0 border border-blue-500/30">
                <img src="/logo.png" alt="peopleOS Logo" className="w-full h-full object-cover" />
              </div>
              <div className="flex flex-col">
                <span className="font-black text-2xl tracking-tighter text-text-primary uppercase whitespace-nowrap leading-none">
                  {config.brandingName}
                </span>
                <span className="text-[11px] font-black text-blue-400 uppercase leading-none mt-1.5 ml-1">
                  e Bussiness Suite
                </span>
              </div>
            </div>
          </div>

          <nav
            className="flex-1 px-4 mt-3 space-y-4 pb-10 min-h-0 overflow-y-auto custom-scrollbar touch-pan-y max-h-[calc(100vh-160px)]"
            style={{ WebkitOverflowScrolling: 'touch' }}
          >
            {filteredNavGroups.map((group, idx) => (
              <div key={idx} className="space-y-1">
                {group.title && (
                  <p className="px-4 text-[9px] font-black text-blue-400/80 uppercase tracking-[0.2em] mb-2 whitespace-nowrap">
                    {group.title}
                  </p>
                )}
                {group.items
                  .filter((item) => config.enabledModules[item.id] !== false)
                  .map((item) => (
                    <button
                      key={item.id}
                      onClick={() => {
                        navigate(`/${item.id}`);
                        if (window.innerWidth < 768) {
                          setSidebarOpen(false);
                        }
                      }}
                      className={`w-full flex items-center gap-3 px-3.5 py-1.5 rounded-xl transition-all duration-300 text-left group/navitem relative overflow-hidden ${
                        activeModule === item.id
                          ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-[0_0_20px_rgba(37,99,235,0.5)] border border-blue-400/50'
                          : 'text-slate-400 hover:bg-slate-800/60 hover:text-blue-400 hover:border-blue-500/10 hover:translate-x-1 border border-transparent'
                      }`}
                      title={item.label}
                    >
                      <div
                        className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 transition-all border ${
                          activeModule === item.id
                            ? 'bg-white border-white shadow-[0_0_10px_rgba(255,255,255,0.8)]'
                            : 'bg-slate-900 border-slate-800 group-hover/navitem:border-blue-500/20'
                        }`}
                      >
                        <item.icon
                          size={14}
                          className={
                            activeModule === item.id
                              ? 'text-blue-600'
                              : 'text-slate-500 group-hover/navitem:text-blue-400'
                          }
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <span
                          className={`font-black text-[0.75rem] uppercase tracking-wide antialiased truncate leading-tight ${
                            activeModule === item.id
                              ? 'text-slate-100'
                              : 'text-slate-400 group-hover/navitem:text-blue-200 transition-colors'
                          }`}
                        >
                          {item.label}
                        </span>
                      </div>
                    </button>
                  ))}
              </div>
            ))}
          </nav>

          <div className="p-4 border-t border-blue-500/20 bg-slate-900/50 shrink-0 mb-4">
            {currentUser && (
              <div className="flex items-center gap-3 p-2 rounded-xl bg-slate-800/50 border border-white/5 mb-3 backdrop-blur-sm transition-colors hover:bg-slate-800/80">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold shadow-lg ring-2 ring-white/10">
                  {currentUser.name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="flex-1 min-w-0">
                  <p
                    className="text-sm font-bold text-slate-200 truncate leading-none"
                    title={currentUser.name}
                  >
                    {currentUser.name || 'User'}
                  </p>
                  <p className="text-[10px] uppercase tracking-wider text-blue-400 font-bold truncate mt-1">
                    {currentUser.userType || 'Guest'}
                  </p>
                </div>
              </div>
            )}

            <div className="grid grid-cols-5 gap-2 mt-3">
              <button
                onClick={toggleTheme}
                className="col-span-1 flex items-center justify-center py-2.5 rounded-xl bg-slate-800 hover:bg-blue-500/10 text-slate-400 hover:text-blue-400 border border-transparent hover:border-blue-500/20 transition-all duration-300 group shadow-sm"
                title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
              >
                {theme === 'dark' ? (
                  <Sun
                    size={18}
                    className="group-hover:rotate-90 transition-transform duration-500"
                  />
                ) : (
                  <Moon
                    size={18}
                    className="group-hover:-rotate-12 transition-transform duration-500"
                  />
                )}
              </button>

              <button
                onClick={onLogout}
                className="col-span-4 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-slate-800 hover:bg-red-500/10 text-slate-400 hover:text-red-400 border border-transparent hover:border-red-500/20 transition-all duration-300 group shadow-sm hover:shadow-red-500/10"
              >
                <LogOut
                  size={16}
                  className="group-hover:scale-110 transition-transform duration-300"
                />
                <span className="text-xs font-black uppercase tracking-widest">Log Out</span>
              </button>
            </div>
          </div>
        </aside>

        <main
          className={`app-main flex-1 flex flex-col bg-bg relative overflow-hidden ${
            hasHydrated ? 'transition-all duration-300' : ''
          }`}
          style={
            hasHydrated
              ? { marginLeft: currentSidebarMargin }
              : sidebar.isOpen
                ? { marginLeft: 280 }
                : { marginLeft: 0 }
          }
        >
          <header className="h-16 bg-surface border-b border-blue-500/20 sticky top-0 z-50 px-8 flex items-center justify-between transition-all duration-300 shrink-0 shadow-lg">
            <div className="flex items-center gap-4">
              <button
                onClick={sidebar.toggle}
                className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400"
                aria-label="Toggle sidebar"
              >
                <Menu size={20} />
              </button>
              <div className="flex items-center gap-3 text-sm font-medium text-text-muted">
                <span className="text-text-primary font-black uppercase tracking-wider text-[0.8rem]">
                  {activeModule}
                </span>
                <span className="text-blue-500/30">/</span>
                <span className="text-text-muted text-[0.7rem] uppercase tracking-wide">
                  Overview
                </span>
              </div>
            </div>

            <div className="flex items-center gap-6">
              {import.meta.env.VITE_APP_ENV !== 'production' &&
                import.meta.env.MODE !== 'production' && (
                  <div
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-full border shadow-inner ${
                      import.meta.env.VITE_APP_ENV === 'development' ||
                      import.meta.env.MODE === 'development'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}
                  >
                    <div
                      className={`w-2 h-2 rounded-full animate-pulse ${
                        import.meta.env.VITE_APP_ENV === 'development' ||
                        import.meta.env.MODE === 'development'
                          ? 'bg-emerald-500'
                          : 'bg-amber-500'
                      }`}
                    ></div>
                    <span className="text-[0.6rem] font-black uppercase tracking-[0.2em]">
                      {import.meta.env.VITE_APP_ENV === 'development' ||
                      import.meta.env.MODE === 'development'
                        ? 'LOCAL DEV'
                        : 'TEST ENV'}
                    </span>
                  </div>
                )}
            </div>

            <div className="flex items-center gap-4">
              <ThemeSwitcher compact={false} />
              <button
                onClick={() => setAIPanelOpen(!isAIPanelOpen)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full border transition-all duration-300 ${
                  isAIPanelOpen
                    ? 'bg-blue-600/20 border-blue-500 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.3)]'
                    : 'bg-slate-800/50 border-white/5 text-slate-400 hover:bg-slate-800 hover:border-blue-500/30'
                }`}
              >
                <BrainCircuit size={16} className={isAIPanelOpen ? 'text-blue-400' : ''} />
                <span className="text-xs font-bold uppercase tracking-wider">
                  {isAIPanelOpen ? 'AI Active' : 'AI Assistant'}
                </span>
              </button>
            </div>
          </header>

          <div className="flex-1 overflow-hidden" style={{ height: 'calc(100vh - 64px)' }}>
            <GlassCard className="m-4 h-full overflow-hidden">
              <div className="h-full overflow-hidden">
                <AppRoutes />
              </div>
            </GlassCard>
          </div>

          <React.Suspense fallback={null}>
            {isAIPanelOpen && (
              <div className="absolute top-16 right-0 w-[400px] h-[calc(100vh-64px)] z-40 animate-in slide-in-from-right duration-300 shadow-2xl">
                <AIInsightsPanel
                  isOpen={isAIPanelOpen}
                  onClose={() => setAIPanelOpen(false)}
                  context="dashboard"
                />
              </div>
            )}
          </React.Suspense>
        </main>
      </div>
    </ToastProvider>
  );
};

export default AuthenticatedApp;
