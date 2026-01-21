# People_OS Database & Environment Standard

> **People_OS treats environments as safety boundaries, not conveniences.**

This is the **authoritative operating model** for the People_OS platform. All contributors must follow these rules.

---

## 1. Environments (Immutable Contract)

People_OS officially recognizes **exactly four** runtime environments:

```
DEV → TEST → STAGE → PROD
```

| Environment | Purpose                   | Data Profile             |
| ----------- | ------------------------- | ------------------------ |
| `DEV`       | Local development         | Synthetic, chaos allowed |
| `TEST`      | Automated testing (CI/CD) | Fixtures, deterministic  |
| `STAGE`     | Production rehearsal      | Anonymized prod snapshot |
| `PROD`      | Live production           | Real, encrypted, audited |

**No shortcuts. No "temporary" environments.**

---

## 2. Database Topology

### Current (SQLite)

```
backend/data/
├── people_os_dev.db
├── people_os_test.db
├── people_os_stage.db
└── people_os_prod.db
```

### Future (PostgreSQL)

```
PostgreSQL Cluster
├── peopleos_dev
├── peopleos_test
├── peopleos_stage
└── peopleos_prod
```

**Rule:** Identical schema structure in every environment.

---

## 3. Schema Structure

All environments share the same schema prefixes:

```
platform_*    (auth, org, user, permission, audit)
hcm_*         (employee, attendance, payroll)
finance_*     (future)
inventory_*   (future)
```

**Rule:** If a table exists in PROD, it exists in DEV/TEST/STAGE.

---

## 4. Roles & Permissions

| Role          | DEV | TEST | STAGE | PROD         |
| ------------- | --- | ---- | ----- | ------------ |
| `dev_user`    | RW  | ❌   | ❌    | ❌           |
| `test_runner` | RW  | RW   | ❌    | ❌           |
| `ci_migrator` | RW  | RW   | RW    | migrate only |
| `app_runtime` | RW  | RW   | RW    | RW           |
| `auditor`     | RO  | RO   | RO    | RO           |
| `human_admin` | RW  | RW   | RW    | controlled   |

**Critical Rule:** No developer has production RW access. Ever.

---

## 5. Migration Discipline

### Rules

- Migrations are **append-only** (no editing old files)
- Rollback scripts required for prod-impacting changes
- Data migrations must be explicit

### Flow

```
DEV → TEST → STAGE → PROD
```

If a migration fails in STAGE, PROD never sees it.

---

## 6. Data Flow Rules

| Direction                 | Allowed? |
| ------------------------- | -------- |
| PROD → STAGE (anonymized) | ✅       |
| STAGE → TEST              | ❌       |
| TEST → DEV                | ❌       |
| DEV → PROD                | ❌       |

**No data flows upward. Only downward (with anonymization).**

---

## 7. Configuration Binding

Required environment variables:

```env
APP_ENV=dev|test|stage|prod   # REQUIRED - App fails without this
DATABASE_URL                  # Optional override
PORT=8000                     # Default
```

**Rule:** If `APP_ENV` is missing, the application MUST NOT start.

---

## 8. CI/CD Promotion Model

```
commit → build → test (peopleos_test) → migrate stage → verify → manual approval → migrate prod → release
```

**Rule:** No manual SQL in production. No exceptions.

---

## 9. Observability Requirements

Each database must emit:

- Slow queries (> 100ms)
- Failed migrations
- Connection spikes
- Lock waits

**Rule:** Prod alerts ≠ Dev alerts.

---

## 10. Enforcement

This standard is enforced by:

1. **Code Guards:** `backend/config.py` validates `APP_ENV` at startup.
2. **Launcher Integration:** `PeopleOS_Launcher.bat` sets `APP_ENV` explicitly.
3. **Audit Checks:** The system audit verifies environment isolation.

---

## Revision History

| Version | Date       | Author | Notes                      |
| ------- | ---------- | ------ | -------------------------- |
| 1.0     | 2026-01-19 | System | Initial authoritative spec |
