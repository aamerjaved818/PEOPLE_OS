
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import json, hashlib, secrets, time, uuid, logging, re
import bcrypt
from datetime import datetime
from fastapi import HTTPException
from typing import Optional, List, Dict, Any

from backend import schemas
from backend import models

logger = logging.getLogger(__name__)
ROOT_USER_ID = "root-system-001"

from backend.dependencies import (
    ROOT_USER_ID, ROOT_USERNAME, ROOT_ROLE,
    AMER_USER_ID, AMER_USERNAME, AMER_ROLE
)

# --- User Management ---

def get_users(db: Session, skip: int = 0, limit: int = 100, current_user: dict = None):
    """
    Get users with visibility filtering based on current_user role.
    Rule: Only Root can see Root user. All other users cannot view Root.
    """
    query = db.query(models.DBUser).offset(skip).limit(limit)
    
    # Filter out Root user if current user is not Root
    if current_user and current_user.get("role") != "Root":
        # Exclude Root user from the results
        query = query.filter(models.DBUser.role != "Root")
    
    users = query.all()

    # Inject In-Memory Root Users if visible (Only for Root role)
    if current_user and current_user.get("role") == "Root":
        # Create synthetic DBUser objects
        # We manually construct these so they appear in the UI list
        root_user = models.DBUser(
            id=ROOT_USER_ID,
            username=ROOT_USERNAME,
            role=ROOT_ROLE,
            is_active=True,
            is_system_user=True,
            name="System Root",
            email="root@system.local",
            organization_id=None
        )
        amer_user = models.DBUser(
             id=AMER_USER_ID,
             username=AMER_USERNAME,
             role=AMER_ROLE,
             is_active=True,
             is_system_user=True,
             name="System Administrator (Amer)",
             email="amer@system.local",
             organization_id=None
        )
        
        # Prepend to list (Reverse order so Root is first)
        users = [root_user, amer_user] + users
        
    return users


def get_user(db: Session, user_id: str, current_user: dict = None):
    """
    Get a single user by ID with visibility filtering.
    Rule: Only Root can access Root user. Others get 404/None.
    """
    user = db.query(models.DBUser).filter(models.DBUser.id == user_id).first()
    
    # If user is Root role and current user is not Root, deny access
    if user and user.role == "Root" and current_user and current_user.get("role") != "Root":
        return None  # Or could raise 404
    
    return user


def get_user_by_username(db: Session, username: str, current_user: dict = None):
    """
    Get user by username with visibility filtering for Root.
    Rule: Only Root can access Root user.
    """
    user = db.query(models.DBUser).filter(models.DBUser.username == username).first()
    
    # If user is Root role and current user is not Root, deny access
    if user and user.role == "Root" and current_user and current_user.get("role") != "Root":
        return None
    
    return user


def create_user(db: Session, user: schemas.UserCreate, creator_id: str = None):
    try:
        # Disallow creating new Root users through the CRUD API to prevent
        # accidental privilege escalation. Root accounts must be created
        # manually by an operator or via protected migration scripts.
        if getattr(user, "role", None) == "Root":
            raise ValueError("Creation of new users with role 'Root' is forbidden")

        # Check if username exists
        existing = get_user_by_username(db, user.username)
        if existing:
            raise ValueError(f"Username {user.username} already exists")

        # Generate ID
        user_id = user.id or str(uuid.uuid4())

        # Hash Password
        pwd_bytes = user.password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

        db_user = models.DBUser(
            id=user_id,
            username=user.username,
            password_hash=hashed_password,
            role=user.role,
            name=getattr(user, "name", None),  # Full name for display
            email=getattr(user, "email", None),  # Email for account recovery
            organization_id=user.organization_id,
            employee_id=user.employee_id,  # Map fields carefully
            is_active=True if user.status == "Active" else False,
            is_system_user=getattr(user, "is_system_user", False),  # System admin flag
            created_by=creator_id,
            updated_by=creator_id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        print(f"Error creating user: {e}")
        raise e


def update_user(
    db: Session, user_id: str, updates: schemas.UserUpdate, updater_id: str
):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = updates.dict(exclude_unset=True)

    # Handle Password Update
    if "password" in update_data and update_data["password"]:
        pwd_bytes = update_data["password"].encode("utf-8")
        salt = bcrypt.gensalt()
        update_data["password_hash"] = bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")
        del update_data["password"]

    # Field Mapping
    if "employeeId" in update_data:
        db_user.employee_id = update_data["employeeId"]
        del update_data["employeeId"]

    if "status" in update_data:
        status_val = update_data["status"]
        if isinstance(status_val, str):
            db_user.is_active = status_val == "Active"
        else:
            db_user.is_active = status_val
        del update_data["status"]

    if "profileStatus" in update_data:
        status_val = update_data["profileStatus"]
        if isinstance(status_val, str):
            db_user.is_active = status_val == "Active"
        del update_data["profileStatus"]

    for field, value in update_data.items():
        if hasattr(db_user, field):
            setattr(db_user, field, value)

    db_user.updated_by = updater_id
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def provision_org_admin(
    db: Session, 
    org: models.DBOrganization, 
    creator_id: str,
    admin_username: str,
    admin_password: str,
    admin_name: Optional[str] = None,
    admin_email: Optional[str] = None
):
    """
    Creates the mandatory super admin for a new organization.
    This is part of the atomic org creation transaction.
    """
    try:
        from backend.dependencies import get_password_hash
        
        target_username = admin_username.lower()
        target_password = admin_password
        
        # Check if username is globally unique (critical for login)
        exists = db.query(models.DBUser).filter(models.DBUser.username == target_username).first()
        if exists:
            raise HTTPException(
                status_code=400,
                detail=f"Admin username '{target_username}' is already taken by another system user."
            )
            
        new_admin = models.DBUser(
            id=str(uuid.uuid4()),
            username=target_username,
            email=admin_email or f"admin@{org.id.lower()}.local",
            password_hash=get_password_hash(target_password),
            name=admin_name or f"Admin {org.name}",
            role="Super Admin",
            organization_id=org.id,
            is_active=True,
            is_system_user=True,
            created_by=creator_id,
            updated_by=creator_id
        )
        db.add(new_admin)
        logger.info(f"Provisioned mandatory super admin '{target_username}' for org '{org.id}'")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to provision mandatory admin for org {org.id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Mandatory Super Admin creation failed: {str(e)}. Organization creation aborted."
        )


# --- Audit Logs ---

def get_audit_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DBAuditLog).offset(skip).limit(limit).all()


def create_audit_log(db: Session, log: schemas.AuditLogCreate):
    db_log = models.DBAuditLog(
        id=f"LOG-{uuid.uuid4()}",
        user=log.user,
        action=log.action,
        status=log.status,
        time=log.time,
        organization_id=log.organization_id,
        details=log.details,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
    
def log_audit_event(db: Session, user, action: str, status: str, details: str = None):
    # Helper to simplify audit logging
    # user can be dict with username and organization_id
    try:
        username = user.get("username", "Unknown") if isinstance(user, dict) else str(user)
        org_id = user.get("organization_id") if isinstance(user, dict) else None
        
        log = schemas.AuditLogCreate(
            user=username,
            action=action,
            status=status,
            time=datetime.now().isoformat(),
            organization_id=org_id,
            details=details
        )
        create_audit_log(db, log)
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}") 


# --- Role Permissions (RBAC) ---

def get_role_permissions(db: Session, role: str):
    return db.query(models.DBRolePermission).filter(models.DBRolePermission.role == role).all()
    
def get_role_permissions_list(db: Session, role: str = None, current_user: dict = None):
    """
    Get role permissions list with Root role visibility filtering.
    Rule: Only Root can see Root permissions. Others cannot query Root permissions.
    """
    # If requesting Root permissions and user is not Root, deny
    if role == "Root" and current_user and current_user.get("role") != "Root":
        return []  # Return empty or could raise 403
    
    if role:
        return db.query(models.DBRolePermission).filter(models.DBRolePermission.role == role).all()
    else:
        # If no role specified, exclude Root permissions unless user is Root
        query = db.query(models.DBRolePermission)
        if current_user and current_user.get("role") != "Root":
            query = query.filter(models.DBRolePermission.role != "Root")
        return query.all()

def update_role_permissions(db: Session, role: str, permissions: List[str]):
    # Delete existing
    db.query(models.DBRolePermission).filter(models.DBRolePermission.role == role).delete()
    
    # Add new
    for p in permissions:
        db_p = models.DBRolePermission(role=role, permission=p)
        db.add(db_p)
    
    db.commit()
    return get_role_permissions(db, role)
    
    
# --- API Keys ---

def _hash_key(key: str) -> str:
    """Hash an API key using SHA256"""
    return hashlib.sha256(key.encode()).hexdigest()

def _generate_key(prefix: str = "hcm") -> str:
    """Generate a secure API key"""
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"

def _get_key_preview(key: str) -> str:
    """Get preview of key: first 8 + last 4 chars"""
    if len(key) <= 12:
        return key
    return f"{key[:8]}...{key[-4:]}"

def create_api_key(db: Session, org_id: str, key_data: schemas.ApiKeyCreate, user_id: str):
    """Create a new API key for organization"""
    raw_key = _generate_key()
    key_hash = _hash_key(raw_key)

    db_key = models.DBApiKey(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        name=key_data.name,
        key_hash=key_hash,
        expires_at=key_data.expires_at,
        created_by=user_id,
        updated_by=user_id,
    )

    db.add(db_key)
    db.commit()
    db.refresh(db_key)

    # Return response with raw key (only shown once)
    return {
        "id": db_key.id,
        "organization_id": db_key.organization_id,
        "name": db_key.name,
        "key_preview": _get_key_preview(raw_key),
        "raw_key": raw_key,  # Only returned at creation
        "last_used": db_key.last_used,
        "revoked": db_key.revoked,
        "expires_at": db_key.expires_at,
        "created_at": db_key.created_at,
        "created_by": db_key.created_by,
    }

def get_api_keys(db: Session, org_id: str, skip: int = 0, limit: int = 50):
    """Get all API keys for an organization (masked)"""
    keys = (
        db.query(models.DBApiKey)
        .filter(
            models.DBApiKey.organization_id == org_id, models.DBApiKey.revoked == False
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": k.id,
            "organization_id": k.organization_id,
            "name": k.name,
            "key_preview": _get_key_preview(k.key_hash[:12]),  # Show prefix only
            "last_used": k.last_used,
            "revoked": k.revoked,
            "expires_at": k.expires_at,
            "created_at": k.created_at,
            "created_by": k.created_by,
        }
        for k in keys
    ]

def revoke_api_key(db: Session, key_id: str):
    """Revoke an API key"""
    db_key = db.query(models.DBApiKey).filter(models.DBApiKey.id == key_id).first()
    if db_key:
        db_key.revoked = True
        db.commit()
        db.refresh(db_key)
    return db_key

def delete_api_key(db: Session, key_id: str):
    """Delete an API key"""
    db_key = db.query(models.DBApiKey).filter(models.DBApiKey.id == key_id).first()
    if db_key:
        db.delete(db_key)
        db.commit()
    return db_key


# --- Webhooks ---

def create_webhook(db: Session, org_id: str, webhook_data: schemas.WebhookCreate, user_id: str):
    db_webhook = models.DBWebhook(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        name=webhook_data.name,
        url=webhook_data.url,
        event_types=json.dumps(webhook_data.event_types),
        headers=json.dumps(webhook_data.headers) if webhook_data.headers else None,
        max_retries=webhook_data.max_retries,
        created_by=user_id,
        updated_by=user_id,
    )

    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)

    return {
        "id": db_webhook.id,
        "organization_id": db_webhook.organization_id,
        "name": db_webhook.name,
        "url": db_webhook.url,
        "event_types": json.loads(db_webhook.event_types),
        "headers": json.loads(db_webhook.headers) if db_webhook.headers else None,
        "is_active": db_webhook.is_active,
        "test_payload_sent": db_webhook.test_payload_sent,
        "last_triggered": db_webhook.last_triggered,
        "failure_count": db_webhook.failure_count,
        "max_retries": db_webhook.max_retries,
        "created_at": db_webhook.created_at,
        "created_by": db_webhook.created_by,
    }

def get_webhooks(db: Session, org_id: str, skip: int = 0, limit: int = 50):
    webhooks = (
        db.query(models.DBWebhook)
        .filter(models.DBWebhook.organization_id == org_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": w.id,
            "organization_id": w.organization_id,
            "name": w.name,
            "url": w.url,
            "event_types": json.loads(w.event_types),
            "headers": json.loads(w.headers) if w.headers else None,
            "is_active": w.is_active,
            "test_payload_sent": w.test_payload_sent,
            "last_triggered": w.last_triggered,
            "failure_count": w.failure_count,
            "max_retries": w.max_retries,
            "created_at": w.created_at,
            "created_by": w.created_by,
        }
        for w in webhooks
    ]

def get_webhook(db: Session, webhook_id: str):
    webhook = (
        db.query(models.DBWebhook).filter(models.DBWebhook.id == webhook_id).first()
    )
    if webhook:
        return {
            "id": webhook.id,
            "organization_id": webhook.organization_id,
            "name": webhook.name,
            "url": webhook.url,
            "event_types": json.loads(webhook.event_types),
            "headers": json.loads(webhook.headers) if webhook.headers else None,
            "is_active": webhook.is_active,
            "test_payload_sent": webhook.test_payload_sent,
            "last_triggered": webhook.last_triggered,
            "failure_count": webhook.failure_count,
            "max_retries": webhook.max_retries,
            "created_at": webhook.created_at,
            "created_by": webhook.created_by,
        }
    return None

def update_webhook(db: Session, webhook_id: str, webhook_data: schemas.WebhookUpdate, user_id: str):
    db_webhook = db.query(models.DBWebhook).filter(models.DBWebhook.id == webhook_id).first()
    if not db_webhook:
        return None

    if webhook_data.name is not None:
        db_webhook.name = webhook_data.name
    if webhook_data.url is not None:
        db_webhook.url = webhook_data.url
    if webhook_data.event_types is not None:
        db_webhook.event_types = json.dumps(webhook_data.event_types)
    if webhook_data.headers is not None:
        db_webhook.headers = json.dumps(webhook_data.headers)
    if webhook_data.is_active is not None:
        db_webhook.is_active = webhook_data.is_active
    if webhook_data.max_retries is not None:
        db_webhook.max_retries = webhook_data.max_retries

    db_webhook.updated_by = user_id
    db.commit()
    db.refresh(db_webhook)
    return get_webhook(db, webhook_id)

def delete_webhook(db: Session, webhook_id: str):
    db_webhook = db.query(models.DBWebhook).filter(models.DBWebhook.id == webhook_id).first()
    if db_webhook:
        db.delete(db_webhook)
        db.commit()
    return db_webhook

def get_webhook_logs(db: Session, webhook_id: str, skip: int = 0, limit: int = 100):
    logs = (
        db.query(models.DBWebhookLog)
        .filter(models.DBWebhookLog.webhook_id == webhook_id)
        .order_by(models.DBWebhookLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": log.id,
            "webhook_id": log.webhook_id,
            "event_type": log.event_type,
            "delivery_status": log.delivery_status,
            "response_status": log.response_status,
            "retry_count": log.retry_count,
            "error_message": log.error_message,
            "created_at": log.created_at,
        }
        for log in logs
    ]

def create_webhook_log(
    db: Session,
    webhook_id: str,
    org_id: str,
    event_type: str,
    payload: dict,
    response_status: int = None,
    response_body: str = None,
    delivery_status: str = "success",
    error_message: str = None,
):
    db_log = models.DBWebhookLog(
        id=str(uuid.uuid4()),
        webhook_id=webhook_id,
        organization_id=org_id,
        event_type=event_type,
        payload=json.dumps(payload),
        response_status=response_status,
        response_body=response_body,
        delivery_status=delivery_status,
        error_message=error_message,
        created_by="system",
        updated_by="system",
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


# --- Background Jobs ---

def create_background_job(db: Session, org_id: str, job_type: str, payload: dict = None, priority: int = 0, user_id: str = "system"):
    db_job = models.DBBackgroundJob(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        job_type=job_type,
        status="queued",
        priority=priority,
        payload=json.dumps(payload) if payload else None,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return _format_background_job(db_job)

def get_background_job(db: Session, job_id: str):
    job = db.query(models.DBBackgroundJob).filter(models.DBBackgroundJob.id == job_id).first()
    if job:
        return _format_background_job(job)
    return None

def get_background_jobs(db: Session, org_id: str, skip: int = 0, limit: int = 50, status: str = None):
    query = db.query(models.DBBackgroundJob).filter(models.DBBackgroundJob.organization_id == org_id)
    if status:
        query = query.filter(models.DBBackgroundJob.status == status)
    jobs = query.order_by(models.DBBackgroundJob.created_at.desc()).offset(skip).limit(limit).all()
    return [_format_background_job(j) for j in jobs]

def update_background_job_status(db: Session, job_id: str, status: str, result: dict = None, error_message: str = None):
    job = db.query(models.DBBackgroundJob).filter(models.DBBackgroundJob.id == job_id).first()
    if not job:
        return None
    
    job.status = status
    if result:
        job.result = json.dumps(result)
    if error_message:
        job.error_message = error_message
    
    if status == "processing":
        job.started_at = datetime.now()
    elif status in ["completed", "failed"]:
        job.completed_at = datetime.now()
    
    job.updated_by = "system"
    db.commit()
    db.refresh(job)
    return _format_background_job(job)

def _format_background_job(db_job) -> dict:
    payload = {}
    result = {}
    if db_job.payload:
        try:
            payload = json.loads(db_job.payload)
        except Exception:
            payload = {}
    if db_job.result:
        try:
            result = json.loads(db_job.result)
        except Exception:
            result = {}
            
    return {
        "id": db_job.id,
        "organization_id": db_job.organization_id,
        "job_type": db_job.job_type,
        "status": db_job.status,
        "priority": db_job.priority,
        "payload": payload,
        "result": result,
        "error_message": db_job.error_message,
        "started_at": db_job.started_at,
        "completed_at": db_job.completed_at,
        "retry_count": db_job.retry_count,
        "max_retries": db_job.max_retries,
        "created_at": db_job.created_at,
    }


# --- System Settings (AI Config, Flags, Notifications) ---

def get_ai_config(db: Session, organization_id: str):
    return db.query(models.DBAIConfiguration).filter(models.DBAIConfiguration.organization_id == organization_id).first()

def update_ai_config(db: Session, organization_id: str, config: schemas.AIConfigurationCreate, user_id: str):
    db_config = get_ai_config(db, organization_id)
    if not db_config:
        db_config = models.DBAIConfiguration(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            provider=config.provider,
            api_keys=json.dumps(config.api_keys) if isinstance(config.api_keys, dict) else config.api_keys,
            status=config.status,
            agents=json.dumps(config.agents) if isinstance(config.agents, dict) else config.agents,
            created_by=user_id,
            updated_by=user_id
        )
        db.add(db_config)
    else:
        db_config.provider = config.provider
        if config.api_keys:
            db_config.api_keys = json.dumps(config.api_keys) if isinstance(config.api_keys, dict) else config.api_keys
        db_config.status = config.status
        db_config.agents = json.dumps(config.agents) if isinstance(config.agents, dict) else config.agents
        db_config.updated_by = user_id
    
    db.commit()
    db.refresh(db_config)
    return db_config

def get_system_flags(db: Session, organization_id: str):
    flags = db.query(models.DBSystemFlags).filter(models.DBSystemFlags.organization_id == organization_id).first()
    if not flags:
        # Check if organization exists before creating flags
        org = db.query(models.DBOrganization).filter(models.DBOrganization.id == organization_id).first()
        if not org:
            return None
        
        flags = models.DBSystemFlags(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            created_by="system",
            updated_by="system"
        )
        db.add(flags)
        db.commit()
        db.refresh(flags)
    return flags

def update_system_flags(db: Session, organization_id: str, flags: schemas.SystemFlagsUpdate, user_id: str):
    db_flags = get_system_flags(db, organization_id)
    if not db_flags:
        db_flags = models.DBSystemFlags(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            created_by=user_id,
        )
        db.add(db_flags)
    
    update_data = flags.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "custom_flags" and isinstance(value, dict):
             setattr(db_flags, field, json.dumps(value))
        elif hasattr(db_flags, field):
            setattr(db_flags, field, value)
    
    db_flags.updated_by = user_id
    db.commit()
    db.refresh(db_flags)
    return db_flags

def get_notification_settings(db: Session, organization_id: str):
    return db.query(models.DBNotificationSettings).filter(models.DBNotificationSettings.organization_id == organization_id).first()

def update_notification_settings(db: Session, organization_id: str, settings: schemas.NotificationSettingsCreate):
    db_settings = get_notification_settings(db, organization_id)
    if not db_settings:
        db_settings = models.DBNotificationSettings(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            # Email
            email_enabled=settings.email_enabled,
            email_provider=settings.email_provider,
            email_from_address=settings.email_from_address,
            email_from_name=settings.email_from_name,
            email_on_employee_created=settings.email_on_employee_created,
            email_on_leave_request=settings.email_on_leave_request,
            email_on_payroll_processed=settings.email_on_payroll_processed,
            email_on_system_alert=settings.email_on_system_alert,
            # SMS
            sms_enabled=settings.sms_enabled,
            sms_provider=settings.sms_provider,
            sms_from_number=settings.sms_from_number
        )
        db.add(db_settings)
    else:
        db_settings.email_enabled = settings.email_enabled
        db_settings.email_provider = settings.email_provider
        db_settings.email_from_address = settings.email_from_address
        db_settings.email_from_name = settings.email_from_name
        db_settings.email_on_employee_created = settings.email_on_employee_created
        db_settings.email_on_leave_request = settings.email_on_leave_request
        db_settings.email_on_payroll_processed = settings.email_on_payroll_processed
        db_settings.email_on_system_alert = settings.email_on_system_alert
        db_settings.sms_enabled = settings.sms_enabled
        db_settings.sms_provider = settings.sms_provider
        db_settings.sms_from_number = settings.sms_from_number
    
    db.commit()
    db.refresh(db_settings)
    return db_settings
