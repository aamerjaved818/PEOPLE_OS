# ADR 002: Modular Domain Architecture

## Context

The system is divided into several independent domains. Each domain must be documented.

## Decision

TheFollowing modules are officially recognized and documented:

1. **Core**: Handles organizations, users, authentication, and platform settings.
2. **HCM**: Human Capital Management (Employees, Attendance, Payroll, Onboarding, Offboarding).
3. **GenAdmin**: General Administration (Asset tracking, office management).
4. **Auth**: Authentication and Authorization layer.
5. **Analytics**: System-wide data processing and reporting.
6. **Self-Service**: Employee-facing features.

Each module must maintain its own `index.tsx` as a public interface.

## Status

Accepted
