"""
People_OS Event Emitter Service

This is the central nervous system of People_OS. Every meaningful
state transition flows through here.

Usage:
    from backend.domains.core.event_emitter import emit_event
    
    emit_event(
        event_type="hcm.employee.created",
        entity_type="employee",
        entity_id=employee.id,
        action="created",
        actor_id=current_user.id,
        payload={"name": employee.name}
    )
"""
import hashlib
import json
import uuid
from datetime import datetime
from typing import Optional

from backend.config import settings
from backend.database import get_engine, get_session_local
from backend.domains.core.models import DBPlatformEvent


def _compute_hash(previous_hash: Optional[str], payload: str) -> str:
    """Compute SHA-256 hash for event chain integrity."""
    data = f"{previous_hash or ''}{payload}{datetime.utcnow().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()


def _get_last_event_hash() -> Optional[str]:
    """Get the hash of the last event in the chain."""
    session = get_session_local()()
    try:
        last_event = session.query(DBPlatformEvent).order_by(
            DBPlatformEvent.timestamp.desc()
        ).first()
        return last_event.event_hash if last_event else None
    finally:
        session.close()


def emit_event(
    event_type: str,
    entity_type: str,
    entity_id: str,
    action: str,
    actor_id: Optional[str] = None,
    actor_type: str = "human",
    organization_id: Optional[str] = None,
    severity: str = "low",
    payload: Optional[dict] = None,
) -> DBPlatformEvent:
    """
    Emit an immutable event to the Event Spine.
    
    This is the ONLY approved way to record state transitions in People_OS.
    
    Args:
        event_type: Namespaced event type (e.g., "hcm.employee.created")
        entity_type: Type of entity affected (e.g., "employee")
        entity_id: UUID of the affected entity
        action: Action taken (created, updated, deleted, approved, etc.)
        actor_id: ID of the user/system that performed the action
        actor_type: "human", "system", or "pipeline"
        organization_id: Organization context
        severity: "low", "medium", "high", "critical"
        payload: Additional event data (JSON-serializable)
    
    Returns:
        The created DBPlatformEvent
    """
    # Validate event_type format: <domain>.<entity>.<action>
    parts = event_type.split(".")
    if len(parts) < 3:
        raise ValueError(
            f"Invalid event_type '{event_type}'. "
            "Must follow <domain>.<entity>.<action> format."
        )
    domain = parts[0]
    
    # Serialize payload
    payload_json = json.dumps(payload) if payload else None
    
    # Build chain integrity
    previous_hash = _get_last_event_hash()
    event_hash = _compute_hash(previous_hash, payload_json or "")
    
    # Create event
    event = DBPlatformEvent(
        id=str(uuid.uuid4()),
        event_type=event_type,
        domain=domain,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor_id=actor_id,
        actor_type=actor_type,
        organization_id=organization_id,
        environment=settings.ENVIRONMENT,
        severity=severity,
        payload=payload_json,
        previous_hash=previous_hash,
        event_hash=event_hash,
    )
    
    # Persist
    session = get_session_local()()
    try:
        session.add(event)
        session.commit()
        session.refresh(event)
        return event
    finally:
        session.close()


def query_events(
    domain: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 100,
) -> list:
    """Query events from the Event Spine."""
    session = get_session_local()()
    try:
        query = session.query(DBPlatformEvent)
        if domain:
            query = query.filter(DBPlatformEvent.domain == domain)
        if entity_type:
            query = query.filter(DBPlatformEvent.entity_type == entity_type)
        if entity_id:
            query = query.filter(DBPlatformEvent.entity_id == entity_id)
        return query.order_by(
            DBPlatformEvent.timestamp.desc()
        ).limit(limit).all()
    finally:
        session.close()
