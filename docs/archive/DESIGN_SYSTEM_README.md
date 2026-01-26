// src/design-system/README.md

# Design System & Theme Guide

## Quick Reference

### Color Tokens (CSS Variables)

#### Light Mode

```css
--bg-app          #f8fafc           /* Page background */
--bg-surface      rgba(255,255,255,0.75)  /* Cards */
--bg-muted        #f1f5f9           /* Muted areas */
--bg-elevated     #ffffff           /* Elevated surfaces */

--text-primary    #0f172a           /* Primary text */
--text-secondary  #475569           /* Secondary text */
--text-muted      #94a3b8           /* Muted text */

--border-default  rgba(148,163,184,0.25)
--border-strong   rgba(148,163,184,0.5)

--primary         #4f46e5           /* Indigo 600 */
--primary-hover   #4338ca
--primary-soft    #e0e7ff
--primary-active  #3730a3

--success         #10b981           /* Emerald */
--warning         #f59e0b           /* Amber */
--danger          #ef4444           /* Red */
--info            #0ea5e9           /* Sky */
```

#### Dark Mode

Same tokens, different values. Applied via `.dark` class on `<html>`.

### Component Classes

#### Glass Surfaces

```html
<div class="glass-card">
  <!-- Premium frosted glass card -->
  <div class="glass-panel"><!-- Elevated glass panel --></div>
</div>
```

#### Inputs & Forms

```html
<input class="input-frost">     <!-- Frosted input styling -->
<select>                        <!-- Auto-themed select -->
<textarea>                      <!-- Auto-themed textarea -->
```

#### Buttons

```html
<button class="btn btn-primary">
  <!-- Primary action button -->
  <button class="btn btn-primary is-verifying"><!-- With loader --></button>
</button>
```

### Using Tokens

#### In Tailwind Classes

```tsx
<div className="bg-surface text-text-primary border border-border">
  <h1 className="text-text-primary font-bold">
    <span className="text-primary">Premium</span> Title
  </h1>
</div>
```

#### In Inline Styles (when needed)

```tsx
<div style={{ color: 'var(--text-muted)' }}>
```

## Migration Checklist

### For Existing Components

- [ ] Replace hardcoded colors with CSS variables
- [ ] Use `glass-card` for surfaces
- [ ] Apply `input-frost` to form inputs
- [ ] Use semantic token classes
- [ ] Test in light AND dark mode
- [ ] Test with each color theme

### Example Migration

**Before:**

```tsx
<div className="bg-white border border-gray-200 p-6 rounded-xl shadow-md">
  <input type="text" className="border border-gray-300 rounded-lg px-4 py-2" />
  <button className="bg-blue-600 text-white px-6 py-2 rounded-full">Submit</button>
</div>
```

**After:**

```tsx
<div className="glass-card p-6">
  <input type="text" className="input-frost" />
  <button className="btn btn-primary">Submit</button>
</div>
```

## Testing Dark Mode

### Browser DevTools

```javascript
// Force dark mode
document.documentElement.classList.add('dark');

// Force light mode
document.documentElement.classList.remove('dark');

// Check current mode
document.documentElement.classList.contains('dark') ? 'dark' : 'light';
```

### In Code

```tsx
import { useTheme } from '@/contexts/ThemeContext';

export const Component = () => {
  const { theme, toggleTheme } = useTheme();

  return <button onClick={toggleTheme}>Current: {theme} - Click to toggle</button>;
};
```

## Color Theme Options

| Theme           | Color   | Best For              |
| --------------- | ------- | --------------------- |
| Cyber (Blue)    | #3b82f6 | Professional, default |
| Quartz (Purple) | #8b5cf6 | Creative, premium     |
| Forest (Green)  | #10b981 | Eco, calm             |
| Sunset (Rose)   | #f43f5e | Modern, energetic     |

Access via `useUIStore()`:

```tsx
const { colorTheme, setColorTheme } = useUIStore();
setColorTheme('forest'); // Changes to green theme
```

## Component Library Status

| Component | Theme-Ready | Notes                     |
| --------- | ----------- | ------------------------- |
| GlassCard | ✅          | Use for all card surfaces |
| Input     | ✅          | Use class="input-frost"   |
| Button    | ⚠️          | Use btn-primary class     |
| Modal     | ✅          | Auto-themed               |
| Card      | ✅          | Use glass-card class      |
| Form      | ✅          | Inputs auto-themed        |

## Accessibility Features

### Automatic

- ✅ WCAG AA contrast in light and dark
- ✅ Keyboard navigation focus states
- ✅ Reduced motion support
- ✅ High contrast on status colors

### Developer Checklist

- [ ] All interactive elements keyboard accessible
- [ ] Proper ARIA labels on buttons/forms
- [ ] Color not sole differentiator
- [ ] 3:1 minimum contrast ratio maintained

## Performance Tips

1. **Use CSS variables** - No runtime overhead
2. **Prefer transform** - Use for animations (GPU-accelerated)
3. **Use will-change sparingly** - Only for complex animations
4. **Backdrop-filter is heavy** - Minimize on low-end devices

## Browser Support

All modern browsers (Chrome 88+, Firefox 85+, Safari 14+, Edge 88+):

- ✅ CSS Custom Properties
- ✅ backdrop-filter
- ✅ CSS Grid & Flexbox
- ✅ CSS Transforms
- ✅ prefers-color-scheme

## Resources

- `src/index.css` - All theme CSS
- `src/contexts/ThemeContext.tsx` - Theme switching logic
- `src/store/uiStore.ts` - Color theme state
  -- `src/components/ui/ThemeSwitcher.tsx` - UI controls
  -- `docs/theme/THEME_DOCUMENTATION.md` - Full theme guide
