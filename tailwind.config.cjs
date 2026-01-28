/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class', '[data-theme="dark"]'],
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
    './modules/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      animation: {
        shine: 'shine 5s linear infinite',
        float: 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        shine: {
          '0%': { backgroundPosition: '200% center' },
          '100%': { backgroundPosition: '-200% center' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',

        // Legacy/Custom mappings mapped to new system
        bg: 'hsl(var(--background))',
        surface: 'hsl(var(--card))',
        'muted-bg': 'hsl(var(--muted))',
        elevated: 'hsl(var(--card))',

        // Sidebar specific (kept as direct vars since they are hex in index.css)
        sidebar: {
          DEFAULT: 'var(--sidebar-bg)',
          surface: 'var(--sidebar-surface)',
          text: 'var(--sidebar-text)',
          muted: 'var(--sidebar-text-muted)',
          border: 'var(--sidebar-border)',
          active: 'var(--sidebar-active)',
        },

        // Vibrant palette (mapped to variables if they exist, or fallbacks)
        vibrant: {
          blue: 'var(--vibrant-blue)',
          pink: 'var(--vibrant-pink)',
          purple: 'var(--vibrant-purple)',
          orange: 'var(--vibrant-orange)',
          cyan: 'var(--vibrant-cyan)',
          green: 'var(--vibrant-green)',
        },
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
