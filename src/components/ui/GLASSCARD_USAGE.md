GlassCard Component — Usage

This lightweight `GlassCard` wrapper provides a reusable frosted glass container with subtle hover effects.

Import:

```tsx
import GlassCard from '@/components/ui/GlassCard';
```

Basic usage:

```tsx
<GlassCard className="p-6 max-w-lg mx-auto">
  <h3 className="text-xl font-bold">Premium Panel</h3>
  <p className="text-sm text-text-muted">Use this for elevated panels and modals.</p>
</GlassCard>
```

Helpful classes provided by `src/index.css`:

- `glass-card` — base glass container
- `input-frost` — frosted input style (use on `input` and `textarea`)
- `btn`, `btn-primary` — primary button styles
- `is-verifying` — add this class to a button to show the inline spinner

Notes:

- `GlassCard` is intentionally tiny and composition-friendly. Add layout classes as needed.
- For accessibility, ensure keyboard focus styles remain visible on interactive children.
