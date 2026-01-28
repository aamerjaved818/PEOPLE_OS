import { useEffect } from 'react';
import { useUIStore } from '@/store/uiStore';

const THEMES = [
  'quartz',
  'cyber',
  'forest',
  'sunset',
  'navy',
  'gold',
  'deeppink',
  'fuchsia',
  'orange',
] as const;

export function ColorThemeManager() {
  const { colorTheme } = useUIStore();

  useEffect(() => {
    const root = document.body;

    // Remove all existing theme classes
    THEMES.forEach((t) => root.classList.remove(`theme-${t}`));

    // Add current theme class
    if (colorTheme) {
      root.classList.add(`theme-${colorTheme}`);
    }
  }, [colorTheme]);

  return null;
}
