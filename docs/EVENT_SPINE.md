# People_OS — Event Spine

> **Nothing meaningful happens without emitting an event.**

The Event Spine is the nervous system of People_OS. Every state transition that matters is recorded as an immutable event, enabling audit, intelligence, compliance, and replay.

---

## Core Principle

If it would matter during an audit, it emits an event.

---

## Event Structure

Each event contains:

| Field             | Description                               |
| ----------------- | ----------------------------------------- |
| `id`              | UUID, immutable                           |
| `event_type`      | Namespaced: `<domain>.<entity>.<action>`  |
| `domain`          | platform, hcm, finance, etc.              |
| `entity_type`     | employee, payroll, user, etc.             |
| `entity_id`       | UUID of the affected entity               |
| `action`          | created, updated, approved, deleted, etc. |
| `actor_id`        | Who performed the action                  |
| `actor_type`      | human, system, pipeline                   |
| `organization_id` | Organization context                      |
| `environment`     | dev, test, stage, prod                    |
| `timestamp`       | UTC timestamp                             |
| `severity`        | low, medium, high, critical               |
| `payload`         | JSON additional data                      |
| `previous_hash`   | Chain integrity                           |
| `event_hash`      | Chain integrity                           |

---

## Namespacing Rules

Event types **must** follow:

```
<domain>.<entity>.<action>
```

### Examples

```
hcm.employee.created
hcm.payroll.approved
platform.permission.revoked
platform.migration.applied
theme.violation.detected
```

No free-form event names. Ever.

---

## Usage

```python
from backend.domains.core.event_emitter import emit_event

# Emit an event
emit_event(
    event_type="hcm.employee.created",
    entity_type="employee",
    entity_id=employee.id,
    action="created",
    actor_id=current_user.id,
    payload={"name": employee.name, "department": employee.department_id}
)
```

---

## Event Integrity

Events are:

- **Immutable**: Once created, never modified
- **Chained**: Each event hash references the previous
- **Time-ordered**: UTC timestamp index
- **Attributable**: Always has an actor

This provides:

- Tamper detection
- Forensic timelines
- Compliance-grade history
- Replay capability

---

## What Emits Events

| Domain     | Events                                              |
| ---------- | --------------------------------------------------- |
| `platform` | user.created, permission.changed, migration.applied |
| `hcm`      | employee.created, payroll.approved, leave.requested |
| `finance`  | invoice.created, payment.processed                  |

---

## Consumers

**Current**:

- Audit logs
- Activity feeds
- Admin dashboards

**Future**:

- Compliance checks
- Drift detection
- Risk scoring
- Predictive alerts

---

## Revision History

| Version | Date       | Notes                             |
| ------- | ---------- | --------------------------------- |
| 1.0     | 2026-01-19 | Initial Event Spine specification |
