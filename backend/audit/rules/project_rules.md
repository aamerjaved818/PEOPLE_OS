# Project Rules

## 1. Single Central Theme Policy

- **Sole Source of Truth**: `src/index.css` is the ONLY allowed location for global theme definitions, CSS variables (`:root`), and global utility classes.
- **No Fragmentation**: Do not create separate CSS files for sub-modules or design systems (e.g., no `theme.css`, `globals.css`).
- **Tailwind Integration**: All global styles must coexist with the Tailwind directives in `index.css`.
- **Enforcement**: Any new CSS file creation must be rejected unless authorized as a localized module-specific exception (which should generally be avoided in favor of Tailwind classes).

## 2. Card Visibility

- **Transparency**: The main layout wrapper must remain transparent. Do not re-introduce global card wrappers (like `GlassCard`) that obscure the background.
- **Contrast**: Ensure all text within cards is fully opaque and high-contrast.

## 3. Technology Stack

- **Styling**: Vanilla CSS (in `index.css`) + Tailwind CSS only. Avoid CSS-in-JS libraries unless necessary.

## 4. Version Control Strategy

- **Manual Authority**: The project version is manually managed. NO automated tools or CI/CD pipelines are permitted to auto-increment the version.
- **Single Source of Truth**: The `VERSION` file in the project root is the master definition of the current version.
- **Synchronization**: `package.json` and `backend/config.py` (via file read) must align with the root `VERSION` file.
- **Decision**: Version bumps (Major.Minor.Patch) are exclusively decided by the Project Lead (User).
