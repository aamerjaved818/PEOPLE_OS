import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    // Check localStorage first
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('people_os_theme');
      if (savedTheme === 'dark' || savedTheme === 'light') {
        return savedTheme;
      }

      // Fallback to system preference
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
    }
    return 'light';
  });

  useEffect(() => {
    // Apply theme class to document root
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(theme);

    // Also set data-theme attribute for CSS compatibility
    root.setAttribute('data-theme', theme);

    // Save preference
    localStorage.setItem('people_os_theme', theme);
  }, [theme]);

  // Sync theme and config across tabs/windows
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (!e.key) {return;}
      if (e.key === 'people_os_theme') {
        if (e.newValue === 'dark' || e.newValue === 'light') {
          setTheme(e.newValue as Theme);
        }
      }
      if (e.key === 'PeopleOS_config') {
        // Broadcast a custom event so app components can react
        window.dispatchEvent(new Event('PeopleOS_config_updated'));
      }
    };

    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
