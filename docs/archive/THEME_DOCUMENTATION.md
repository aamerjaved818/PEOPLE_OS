# PEOPLE_OS Theme System

## Overview

PEOPLE_OS features a **comprehensive, accessible, and premium theme system** with:

- ✅ Light and Dark modes with automatic system preference detection
- ✅ 4 color themes: Cyber (Blue), Quartz (Purple), Forest (Green), Sunset (Rose)
- ✅ Glassmorphic design tokens throughout

# MOVED: Theme documentation relocated to `docs/theme/`

This file has been moved to the repository `docs/` folder to keep the project root clean.

- New location: `docs/theme/THEME_DOCUMENTATION.md`

Please open that file for the full theme documentation and usage guides.

Submit
</button>

````

**Glass Cards:**

```tsx
<div className="glass-card p-6">
  <input className="input-frost" placeholder="Type here..." />
</div>
````

### Form Controls

All inputs, selects, and textareas automatically inherit theme styling:

```tsx
<input type="text" placeholder="Theme-aware input" />
<textarea placeholder="Theme-aware textarea"></textarea>
<select>
  <option>Theme-aware select</option>
</select>
```

**Special:** Use `.input-frost` class for extra frosted appearance:

```tsx
<input type="text" className="input-frost" placeholder="Frosted input" />
```

### Buttons with Verification Animation

Add `.is-verifying` class to show spinner:

```tsx
<button className={`btn btn-primary ${isVerifying ? 'is-verifying' : ''}`}>
  <span className="label">Submit</span>
</button>
```

CSS generates:

- Spinning loader animation
- Subtle text pulse
- Disabled pointer-events

## Styling Best Practices

### ✅ DO

1. **Use semantic tokens** instead of hardcoded colors:

   ```tsx
   // ✅ Good
   <div className="text-text-primary bg-surface">

   // ❌ Bad
   <div className="text-blue-900 bg-white">
   ```

2. **Leverage glass components** for premium look:

   ```tsx
   // ✅ Good
   <div className="glass-card p-6">

   // ❌ Bad
   <div className="bg-white border-gray-200 p-6">
   ```

3. **Use shadow tokens** for depth:

   ```tsx
   // ✅ Good
   <div className="shadow-lg">

   // ❌ Bad
   <div style={{boxShadow: '0 10px 30px rgba(0,0,0,0.2)'}}>
   ```

4. **Apply theme to interactive elements**:
   ```tsx
   <button className="bg-primary text-primary-foreground hover:bg-primary-hover">
   ```

### ❌ DON'T

1. ❌ Hardcode colors - breaks theme switching
2. ❌ Use deprecated color classes (e.g., `bg-blue-500`)
3. ❌ Mix theme systems (CSS vars + Tailwind colors)
4. ❌ Forget hover states for interactive elements

## Accessibility

### Reduced Motion Support

Automatically disables animations for users with `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  body::before {
    animation: none;
  }
  .glass-card,
  .btn {
    transition: none;
  }
}
```

### Color Contrast

Semantic tokens ensure:

- ✅ WCAG AA contrast ratios (light/dark modes)
- ✅ Focus states for keyboard navigation
- ✅ High visibility status colors

### ARIA Labels

Buttons include appropriate labels:

```tsx
<button aria-label="Toggle theme">
  <Moon className="w-5 h-5" />
</button>
```

## Component Coverage

### Fully Theme-Aware ✅

- Login form (`Login.tsx`)
- All modals and dialogs
- Card components (`GlassCard`)
- Input fields (text, select, textarea)
- Buttons and action elements
- System audit/log viewers
- Dashboard panels

### Form Controls

Global styles apply theme to:

- `<input type="text|email|password|number|date|time" />`
- `<textarea>`
- `<select>`

Excludes decorative inputs:

- Checkboxes, radio buttons (use custom components)
- File inputs (use custom components)
- Range sliders (use custom components)

## Animation System

### Built-in Animations

| Animation    | Duration | Purpose                 |
| ------------ | -------- | ----------------------- |
| `drift`      | 18s      | Subtle background drift |
| `spin`       | 900ms    | Button loading spinner  |
| `pulse-text` | 1.2s     | Verifying state text    |
| `fade-in`    | 500ms    | Modal entrance          |
| `zoom-in-95` | 500ms    | Scale entrance          |

### Customization

All transitions use `--transition-base: 250ms cubic-bezier(0.2, 0.9, 0.2, 1)`:

```css
/* Smooth, snappy easing curve */
transition: all var(--transition-base);
```

## Extending the Theme

### Adding a New Color Theme

1. Add CSS variables in `src/index.css`:

```css
body.theme-custom {
  --primary: #your-color;
  --primary-hover: #darker-shade;
  --primary-soft: #lighter-shade;
  /* ... */
}

.dark body.theme-custom {
  --primary: #dark-variant;
  /* ... */
}
```

2. Update `COLOR_THEMES` in `ThemeSwitcher.tsx`:

```tsx
{ id: 'custom', label: 'Custom', color: '#your-color' }
```

3. Update theme options in `uiStore` if needed

### Adding a New Semantic Token

1. Define in `:root` and `.dark`:

```css
--my-new-token: #value;
```

2. Use in components:

```tsx
<div className="text-[var(--my-new-token)]">
```

Or with Tailwind (if CSS variable is available):

```tsx
<div style={{ color: 'var(--my-new-token)' }}>
```

## File Structure

```
src/
├── index.css                          # Theme tokens & glassmorphic styles
├── design-system/theme.css            # Additional theme definitions
├── contexts/
│   └── ThemeContext.tsx              # Light/Dark mode context
├── store/
│   └── uiStore.ts                    # Color theme store
├── components/ui/
│   ├── GlassCard.tsx                 # Glass card component
│   ├── Input.tsx                     # Theme-aware input
│   └── ThemeSwitcher.tsx             # Theme control UI
└── modules/
    └── ... (all using theme tokens)
```

## Testing Theme

### Manual Testing Checklist

- [ ] Light mode displays correctly
- [ ] Dark mode displays correctly
- [ ] All color themes apply properly
- [ ] Glassmorphic elements visible
- [ ] Form controls inherit theme
- [ ] Buttons have hover states
- [ ] Modals/cards use glass style
- [ ] Text contrast meets WCAG AA
- [ ] Animations work (non-reduced motion)
- [ ] Animations disabled (reduced motion)
- [ ] Theme persists on page reload
- [ ] Theme syncs across tabs

### Browser DevTools

To manually test theme tokens:

```javascript
// Check current theme
document.documentElement.classList.contains('dark');

// Check color theme
window.getComputedStyle(document.body).getPropertyValue('--primary');

// Apply theme programmatically
document.documentElement.classList.add('dark');
document.body.classList.add('theme-forest');
```

## Performance Notes

- ✅ CSS variables are performant (no runtime calculations)
- ✅ Backdrop blur uses hardware acceleration
- ✅ Animations use transform (GPU-accelerated)
- ✅ No JavaScript overhead for theme switching
- ✅ Minimal bundle size impact

## Browser Support

| Feature                | Chrome | Firefox | Safari | Edge |
| ---------------------- | ------ | ------- | ------ | ---- |
| CSS Variables          | ✅     | ✅      | ✅     | ✅   |
| Backdrop-filter        | ✅     | ✅      | ✅     | ✅   |
| Prefers-color-scheme   | ✅     | ✅      | ✅     | ✅   |
| Prefers-reduced-motion | ✅     | ✅      | ✅     | ✅   |

## Support & Troubleshooting

### Theme Not Applying?

1. Check that `ThemeProvider` wraps your app in `main.tsx`
2. Verify CSS is loaded (check `index.css` import)
3. Clear browser cache and localStorage
4. Check browser console for errors

### Dark Mode Not Working?

1. Ensure `.dark` class is on `<html>` element
2. Check `ThemeContext` is providing theme correctly
3. Verify CSS dark mode variables are defined

### Custom Theme Not Showing?

1. Check color theme class applied to body
2. Verify custom theme CSS in `index.css`
3. Clear localStorage and reload
4. Check UIStore is updating correctly

## Future Enhancements

- [ ] Theme gradient preset customization
- [ ] Custom color palette builder UI
- [ ] Per-module theme overrides
- [ ] Animation speed preferences
- [ ] High contrast mode
- [ ] Monochrome/grayscale option

---

**Last Updated:** January 25, 2026
**Theme Version:** 1.0 Premium
