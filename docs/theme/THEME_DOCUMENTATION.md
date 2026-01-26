````markdown
# PEOPLE_OS Theme System

## Overview

PEOPLE_OS features a **comprehensive, accessible, and premium theme system** with:

- ✅ Light and Dark modes with automatic system preference detection
- ✅ 4 color themes: Cyber (Blue), Quartz (Purple), Forest (Green), Sunset (Rose)
- ✅ Glassmorphic design tokens throughout
- ✅ Semantic CSS variables for consistent styling
- ✅ Accessibility-first approach (prefers-reduced-motion support)

## Theme Architecture

### 1. CSS Foundation (`src/index.css`)

#### Semantic Token System

All theme-aware styling uses CSS custom properties (variables):

```css
/* Light Mode (Default) */
:root {
  --bg-app: #f8fafc; /* Page background */
  --bg-surface: rgba(255, 255, 255, 0.75); /* Cards/surfaces (glass) */
  --bg-muted: #f1f5f9; /* Muted backgrounds */
  --bg-elevated: #ffffff;

  --text-primary: #0f172a; /* Primary text */
  --text-secondary: #475569; /* Secondary text */
  --text-muted: #94a3b8; /* Muted text */

  --border-default: rgba(148, 163, 184, 0.25);
  --border-strong: rgba(148, 163, 184, 0.5);

  --primary: #4f46e5; /* Brand color (Indigo) */
  --primary-hover: #4338ca;
  --primary-soft: #e0e7ff;

  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --info: #0ea5e9;
}

/* Dark Mode */
.dark {
  --bg-app: #020617;
  --bg-surface: rgba(15, 23, 42, 0.65);
  /* ... other dark variables */
}
```
````

#### Glassmorphic Components

- `.glass-card` - Premium frosted glass card with backdrop blur
- `.glass-panel` - Elevated glass panel with gradient
- `.input-frost` - Theme-aware input with frosted appearance
- `.btn-primary` - Primary button with gradient and shadow

... (trimmed, content identical to root copy)

```

```
