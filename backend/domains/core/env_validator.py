"""
People_OS Environment Fingerprint Validator

At startup, People_OS validates that the running environment (APP_ENV)
matches the fingerprint stored in the database. This prevents:
- Copied connection strings
- Misconfigured containers
- Human error at 2am

If mismatch detected → hard crash.
"""
import hashlib
import sys
import uuid
from datetime import datetime

from backend.config import settings, VALID_ENVIRONMENTS
from backend.database import get_engine, get_session_local
from backend.domains.core.models import DBPlatformEnvironment
from backend.logging_config import logger


def _compute_fingerprint_checksum(env_name: str) -> str:
    """Compute checksum for environment fingerprint."""
    data = f"{env_name}:{datetime.utcnow().date().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def initialize_environment_fingerprint() -> None:
    """
    Initialize the environment fingerprint for the current database.
    
    Called once during initial database setup. Creates an immutable
    record of which environment this database belongs to.
    """
    session = get_session_local()()
    try:
        existing = session.query(DBPlatformEnvironment).first()
        if existing:
            logger.info(f"[ENV] Database already fingerprinted: {existing.env_name}")
            return
        
        env_name = settings.ENVIRONMENT
        fingerprint = DBPlatformEnvironment(
            id=str(uuid.uuid4()),
            env_name=env_name,
            checksum=_compute_fingerprint_checksum(env_name),
            locked=True,
        )
        session.add(fingerprint)
        session.commit()
        logger.info(f"[ENV] Database fingerprinted as: {env_name}")
    finally:
        session.close()


def validate_environment_fingerprint() -> bool:
    """
    Validate that APP_ENV matches the database fingerprint.
    
    Returns True if valid, exits with FATAL if mismatch detected.
    """
    session = get_session_local()()
    try:
        fingerprint = session.query(DBPlatformEnvironment).first()
        
        if fingerprint is None:
            # New database - initialize fingerprint
            initialize_environment_fingerprint()
            return True
        
        current_env = settings.ENVIRONMENT
        db_env = fingerprint.env_name
        
        if current_env != db_env:
            logger.critical(
                f"FATAL: Environment mismatch!\n"
                f"  APP_ENV={current_env}\n"
                f"  Database fingerprint={db_env}\n"
                f"\n"
                f"This database belongs to the '{db_env}' environment.\n"
                f"You are trying to connect with APP_ENV='{current_env}'.\n"
                f"\n"
                f"This is a HARD BLOCK to prevent data corruption."
            )
            sys.exit(1)
        
        logger.info(f"[ENV] Environment validated: {current_env}")
        return True
    finally:
        session.close()


def get_environment_info() -> dict:
    """Get environment fingerprint information."""
    session = get_session_local()()
    try:
        fingerprint = session.query(DBPlatformEnvironment).first()
        if fingerprint:
            return {
                "env_name": fingerprint.env_name,
                "created_at": str(fingerprint.created_at),
                "checksum": fingerprint.checksum,
                "locked": fingerprint.locked,
            }
        return {"status": "not_initialized"}
    finally:
        session.close()
