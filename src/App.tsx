import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import ErrorBoundary from './components/ErrorBoundary';
import Loading from './components/ui/Loading';
import { ToastProvider } from './components/ui/Toast';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RBACProvider } from './contexts/RBACContext';
import { LayoutProvider } from './contexts/LayoutContext';

// Core Layout
const AuthenticatedApp = React.lazy(() => import('./components/layout/AuthenticatedApp'));
const Login = React.lazy(() => import('./modules/auth/Login'));

import { useOrgStore } from './store/orgStore';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const { currentUser, setCurrentUser } = useOrgStore();

  // Listen for auth:logout event from ApiService
  React.useEffect(() => {
    const handleLogout = () => {
      setCurrentUser(null);
      window.location.href = '/login';
    };
    window.addEventListener('auth:logout', handleLogout);
    return () => window.removeEventListener('auth:logout', handleLogout);
  }, [setCurrentUser]);

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <RBACProvider>
            <LayoutProvider>
              <ToastProvider>
                <BrowserRouter>
                  <Suspense fallback={<Loading size="lg" message="Initializing System..." />}>
                    <Routes>
                      {/* Public Routes */}
                      <Route
                        path="/login"
                        element={
                          currentUser ? (
                            <Navigate to="/dashboard" replace />
                          ) : (
                            <Login onLogin={() => (window.location.href = '/dashboard')} />
                          )
                        }
                      />

                      {/* Protected Routes */}
                      <Route
                        path="/*"
                        element={
                          currentUser ? (
                            <AuthenticatedApp
                              onLogout={() => {
                                setCurrentUser(null);
                                window.location.href = '/login';
                              }}
                            />
                          ) : (
                            <Navigate to="/login" replace />
                          )
                        }
                      />
                    </Routes>
                  </Suspense>
                </BrowserRouter>
              </ToastProvider>
            </LayoutProvider>
          </RBACProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
