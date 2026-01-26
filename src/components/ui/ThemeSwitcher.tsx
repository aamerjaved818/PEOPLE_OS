/**
 * ThemeSwitcher - Toggle between light/dark mode and select color themes
 * Integrates with ThemeContext and UIStore for centralized theme management
 */

import React, { useState } from 'react';
import { Moon, Sun, Palette } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { useUIStore } from '@/store/uiStore';

const COLOR_THEMES = [
  { id: 'cyber', label: 'Cyber (Blue)', color: '#3b82f6' },
  { id: 'quartz', label: 'Quartz (Purple)', color: '#8b5cf6' },
  { id: 'forest', label: 'Forest (Green)', color: '#10b981' },
  { id: 'sunset', label: 'Sunset (Rose)', color: '#f43f5e' },
  { id: 'navy', label: 'Navy (Deep)', color: '#0b2545' },
  { id: 'gold', label: 'Gold (Metallic)', color: '#d4af37' },
  { id: 'deeppink', label: 'DeepPink (Energetic)', color: '#ff1493' },
  { id: 'fuchsia', label: 'Fuchsia (Neon)', color: '#d946ef' },
  { id: 'orange', label: 'Orange (Warm)', color: '#f97316' },
] as const;

interface ThemeSwitcherProps {
  className?: string;
  compact?: boolean;
}

const ThemeSwitcher: React.FC<ThemeSwitcherProps> = ({ className = '', compact = false }) => {
  const { theme, toggleTheme } = useTheme();
  const { colorTheme, setColorTheme } = useUIStore();
  const [showColorPicker, setShowColorPicker] = useState(false);

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Theme Toggle Button (Light/Dark) */}
      <button
        onClick={toggleTheme}
        className="p-2.5 rounded-lg bg-surface border border-border hover:border-primary transition-all duration-300 group"
        title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        aria-label="Toggle theme"
      >
        {theme === 'light' ? (
          <Moon className="w-5 h-5 text-text-primary group-hover:text-primary transition-colors" />
        ) : (
          <Sun className="w-5 h-5 text-text-primary group-hover:text-primary transition-colors" />
        )}
      </button>

      {/* Color Theme Selector */}
      {!compact && (
        <div className="relative">
          <button
            onClick={() => setShowColorPicker(!showColorPicker)}
            className="p-2.5 rounded-lg bg-surface border border-border hover:border-primary transition-all duration-300 group"
            title="Change color theme"
            aria-label="Color theme picker"
          >
            <Palette className="w-5 h-5 text-text-primary group-hover:text-primary transition-colors" />
          </button>

          {/* Color Theme Dropdown */}
          {showColorPicker && (
            <div className="absolute right-0 mt-2 p-3 bg-elevated border border-border rounded-lg shadow-lg z-50 min-w-max">
              <div className="flex flex-col gap-2">
                {COLOR_THEMES.map((colorThemeOption) => (
                  <button
                    key={colorThemeOption.id}
                    onClick={() => {
                      setColorTheme(colorThemeOption.id);
                      setShowColorPicker(false);
                    }}
                    className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-300 ${
                      colorTheme === colorThemeOption.id
                        ? 'bg-primary/20 border border-primary'
                        : 'bg-surface border border-border hover:border-primary/50'
                    }`}
                  >
                    <div
                      className="w-4 h-4 rounded-full border-2 border-current"
                      style={{ backgroundColor: colorThemeOption.color }}
                    />
                    <span className="text-sm font-medium text-text-primary">
                      {colorThemeOption.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ThemeSwitcher;
