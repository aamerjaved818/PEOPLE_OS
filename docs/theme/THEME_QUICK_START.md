````markdown
# Theme System Quick Start

## For End Users

### Toggle Dark/Light Mode

Click the **Moon/Sun icon** in the top header to switch between light and dark modes.

### Change Color Theme

Click the **Palette icon** in the header to choose your color theme:

- **Cyber** (Blue) - Professional default
- **Quartz** (Purple) - Creative premium
- **Forest** (Green) - Eco-friendly calm
- **Sunset** (Rose) - Modern energetic

Your preference is saved automatically!

---

## For Developers

### 1. Use Theme Tokens in New Components

Instead of hardcoding colors, use CSS variable classes:

```tsx
// ❌ WRONG - Hardcoded colors
<div className="bg-white text-blue-900 border border-gray-300">
  <input className="bg-white border border-gray-300" />
</div>

// ✅ RIGHT - Theme tokens
<div className="bg-surface text-text-primary border border-border">
  <input className="input-frost" />
</div>
```
````

... (trimmed, content identical to root copy)

```

```
