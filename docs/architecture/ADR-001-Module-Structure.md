# ADR 001: Standardized Module Structure

## Context

The PeopleOS project requires a standardized way to organize frontend modules (Auth, HCM, etc.) to ensure scalability and maintainability.

## Decision

All frontend modules must reside under `src/modules/{module_name}` and follow this structure:

- `index.tsx`: Public entry point (exports main components)
- `components/`: Module-specific internal components
- `services/`: Module-specific API services (using centralized `api` client)
- `hooks/`: Module-specific React hooks

## Status

Accepted

## Consequences

- Every module must have an `index.tsx`.
- Circular dependencies between modules should be avoided.
- Direct repository or database access from UI is prohibited.
