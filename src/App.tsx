import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { secureStorage } from './utils/secureStorage';
import { RBACProvider } from '@/contexts/RBACContext';
import { LayoutProvider } from '@/contexts/LayoutContext';
import ModuleSkeleton from './components/ui/ModuleSkeleton';
import SplashScreen from './components/ui/SplashScreen'; // New
import { useTheme, ThemeProvider } from './contexts/ThemeContext';
import { useUIStore } from './store/uiStore';
import { useOrgStore } from './store/orgStore';

// Lazy Load Core Components
const Login = React.lazy(() => import('./modules/auth/Login'));
const AuthenticatedApp = React.lazy(() => import('./components/layout/AuthenticatedApp'));

const AppContent: React.FC = () => {
  const { colorTheme, setActiveModule } = useUIStore();
  const { fetchMasterData, fetchProfile, refreshCurrentUser } = useOrgStore();

  const [isInitializing, setIsInitializing] = useState(true);
  const [loadingStatus, setLoadingStatus] = useState('Initializing Application...');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Unified Bootstrap Process
  const bootstrap = useCallback(async () => {
    try {
      // 1. Data Integrity Check (Simplified)
      setLoadingStatus('Verifying Data Integrity...');

      // 2. Auth Verification
      setLoadingStatus('Authenticating Security Node...');
      const token = secureStorage.getItem('token');
      if (token) {
        setIsAuthenticated(true);

        // 3. Parallel Data Fetching for Authenticated Users
        setLoadingStatus('Fetching Core Intelligence...');
        await Promise.all([refreshCurrentUser(), fetchMasterData(), fetchProfile()]).catch((err) =>
          console.warn('Non-critical initialization error:', err)
        );
      } else {
        setIsAuthenticated(false);
      }

      // 4. Finalizing
      setLoadingStatus('Activating Neural Interface...');
      // Small artificial delay for smooth transition
      await new Promise((r) => setTimeout(r, 600));
      setIsInitializing(false);
    } catch (error) {
      console.error('Fatal Bootstrap Error:', error);
      setLoadingStatus('Error: Protocol Failed. Re-authenticating...');
      setTimeout(() => window.location.reload(), 2000);
    }
  }, [fetchMasterData, fetchProfile, refreshCurrentUser]);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  // Theme Sync
  // Theme is applied centrally by ThemeContext; avoid duplicating DOM mutations here.

  // Apply Color Theme
  useEffect(() => {
    document.body.classList.remove('theme-quartz', 'theme-cyber', 'theme-forest', 'theme-sunset');
    document.body.classList.add(`theme-${colorTheme}`);
  }, [colorTheme]);

  // Listen for global logout events
  useEffect(() => {
    const handleGlobalLogout = () => {
      handleLogout();
    };
    window.addEventListener('auth:logout', handleGlobalLogout);
    return () => window.removeEventListener('auth:logout', handleGlobalLogout);
  }, []);

  const handleLogin = async () => {
    setIsAuthenticated(true);
    setIsInitializing(true);
    await bootstrap();
    setActiveModule('dashboard');
  };

  const handleLogout = () => {
    secureStorage.removeItem('token');
    secureStorage.removeItem('current_user');
    setIsAuthenticated(false);
  };

  // 1. Splash Screen Phase
  if (isInitializing) {
    return <SplashScreen status={loadingStatus} />;
  }

  // 2. Auth Phase
  if (!isAuthenticated) {
    return (
      <React.Suspense fallback={<ModuleSkeleton />}>
        <Login onLogin={handleLogin} />
      </React.Suspense>
    );
  }

  // 3. Application Phase
  return (
    <React.Suspense fallback={<ModuleSkeleton />}>
      <AuthenticatedApp onLogout={handleLogout} />
    </React.Suspense>
  );
};

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

// ...

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <LayoutProvider>
          <RBACProvider>
            <ThemeProvider>
              <AppContent />
            </ThemeProvider>
          </RBACProvider>
        </LayoutProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
