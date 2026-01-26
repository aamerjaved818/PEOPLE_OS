# Changelog

## Unreleased

### Fixed

- Handle system/root users without an `organization_id` in `backend/routers/system.py` to prevent 500 errors when fetching system flags.
- Debounced organization/profile fetches in `src/store/orgStore.ts` to prevent request storms during rapid UI actions.
- Applied adaptive client-side rate-limit clamp only in non-production in `src/system/systemStore.ts` to avoid accidental client self-throttling.
