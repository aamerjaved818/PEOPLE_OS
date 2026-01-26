Title: fix(system): handle root org-less requests; debounce org/profile fetches; dev-only rate-limit clamp

Overview:
This PR fixes two stability issues observed in development and testing:

- Backend: endpoints that assumed an `organization_id` for system/root users produced 500 errors. The router now handles `organization_id == None` (Root/system users) and returns sensible defaults when no org exists.
- Frontend: the adaptive rate-limit clamp could reduce the client-side limit too low in development, causing self-throttling and UI errors. The clamp is now applied only in non-production environments. Also, `fetchProfile` has a 300ms debounce to batch rapid organization/profile requests.

Files to review:

- `backend/routers/system.py`
- `src/store/orgStore.ts`
- `src/system/systemStore.ts`

Testing done:

- `python system_test.py` — all tests passed (health, auth, system flags, payroll settings, users, organizations, CORS).
- Manual check: `/api/users` returns 3 users; `/api/system/flags` and `/api/payroll-settings` return 200.
- Frontend behavior: debounced `fetchProfile` prevents request storms; adaptive clamp limited to dev prevents accidental 429s during local development.

How to test locally:

1. Start backend: `python -m backend.main`
2. Start frontend dev server: `npm run dev`
3. Run system tests: `python system_test.py`
4. In browser, open `http://localhost:5173`, hard refresh, and log in with `root` / `root`.
5. Navigate to System Settings → Access Control → System Administrators and confirm `.amer` and `root` are visible and stable.

Notes:

- Consider applying debounce/throttle to other high-frequency fetchers as a follow-up.
- Consider exposing the adaptive clamp via a runtime config or feature flag for staging tuning.
