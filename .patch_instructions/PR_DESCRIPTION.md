Title: fix(system): handle root org-less requests; debounce org/profile fetches; dev-only rate-limit clamp

Summary:

- Fixes backend endpoints that assumed an organization_id for system/root users to avoid 500 errors when `organization_id` is None.
- Adds a 300ms debounce to `fetchProfile` in `src/store/orgStore.ts` to batch rapid org/profile requests.
- Makes the frontend adaptive rate-limit clamp (`Math.max(200, computed)`) apply only in non-production (dev/test), preventing accidental client self-throttling during development.

Files changed:

- `backend/routers/system.py` — handle root/system users without an org and return sensible default flags when no org exists.
- `src/store/orgStore.ts` — debounced `fetchProfile` implementation to queue callers and issue a single network request.
- `src/system/systemStore.ts` — guard adaptive rate-limit clamp to non-production environments.

Testing performed:

- Ran `python system_test.py` — all checks passed (health, auth, system flags, payroll settings, users, organizations, CORS).
- Verified via `monitor_api.py` that `/users` returns 3 users and `/system/flags` and `/payroll-settings` return 200.

Notes / Recommendations:

- Consider adding debounce/throttle to other high-frequency fetchers (e.g., organizations list, master data loaders) to further reduce request spikes.
- Consider making the adaptive clamp behind a runtime feature flag for easier tuning in staging vs production.

How to review:

- Run `python system_test.py` locally after switching to the branch and verify tests pass.
- Open the System Settings → Access Control → System Administrators in the frontend and confirm `.amer` and `root` appear without blinking.

CI / PR checks to include:

- Run unit tests (if available)
- Linting for TypeScript files
- Quick E2E smoke: start backend + frontend and run `system_test.py`

Signed-off-by: Automated assistant
