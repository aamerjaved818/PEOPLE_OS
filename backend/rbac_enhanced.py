"""
Enhanced RBAC Implementation Module
===================================

Provides standardized, enterprise-grade role-based access control with:
- Root (system-level) & Super Admin (organization-level) separation
- Comprehensive validation and audit trails
- Role hierarchy enforcement
- Permission matrix management

This module should be used alongside permissions_config.py for unified RBAC.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from backend.shared.models import models
from backend.permissions_config import ROLE_HIERARCHY, SUPER_ROLES, is_higher_role
from backend.dependencies import get_password_hash, log_audit_event

logger = logging.getLogger(__name__)

# ============================================================
# VALIDATION & ENFORCEMENT
# ============================================================

def validate_root_user_creation(db: Session) -> bool:
    """
    Validate that no duplicate Root user exists in database.
    Root is a special in-memory user and should never appear in DB.
    
    Returns: True if valid (no Root in DB), False otherwise
    """
    existing_root = db.query(models.DBUser).filter(
        models.DBUser.role == "Root",
        models.DBUser.is_system_user == True
    ).first()
    
    if existing_root:
        logger.error(f"SECURITY VIOLATION: Root user found in DB: {existing_root.id}")
        return False
    
    return True


def validate_super_admin_uniqueness(
    db: Session, 
    org_id: str, 
    exclude_user_id: Optional[str] = None
) -> bool:
    """
    Validate that organization has exactly one Super Admin.
    
    Args:
        db: Database session
        org_id: Organization ID
        exclude_user_id: User ID to exclude (for updates)
    
    Returns: True if validation passes
    """
    query = db.query(models.DBUser).filter(
        models.DBUser.organization_id == org_id,
        models.DBUser.role == "Super Admin"
    )
    
    if exclude_user_id:
        query = query.filter(models.DBUser.id != exclude_user_id)
    
    count = query.count()
    return count <= 1  # Should be 0 before creation or 1 after


def validate_system_user_isolation(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that system users are properly isolated from organizations.
    
    Rule: is_system_user=True ↔ organization_id=NULL
    
    Args:
        user_data: User data dictionary
    
    Returns: Validation result with 'valid' and 'errors' keys
    """
    errors = []
    
    is_system = user_data.get("is_system_user", False)
    org_id = user_data.get("organization_id")
    role = user_data.get("role")
    
    # Rule 1: System users cannot have organization_id
    if is_system and org_id:
        errors.append("System users cannot be assigned to organizations")
    
    # Rule 2: Organization users must have organization_id
    if not is_system and not org_id and role not in ["Root"]:
        errors.append(f"Non-system role '{role}' requires organization assignment")
    
    # Rule 3: Super Admin must be organization user
    if role == "Super Admin" and is_system:
        errors.append("Super Admin must be an organization user (is_system_user=False)")
    
    # Rule 4: Root should never be marked as is_system_user in DB
    if role == "Root" and is_system:
        errors.append("Root user should not exist in database")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_organization_exists(db: Session, org_id: str) -> models.DBOrganization:
    """
    Validate that organization exists and return it.
    
    Raises: HTTPException if not found
    """
    org = db.query(models.DBOrganization).filter(
        models.DBOrganization.id == org_id
    ).first()
    
    if not org:
        raise HTTPException(
            status_code=404,
            detail=f"Organization '{org_id}' not found"
        )
    
    return org


def validate_creator_authority(
    creator_role: Optional[str],
    target_role: str
) -> bool:
    """
    Validate that creator has authority to create/modify target role.
    
    Rules:
    - Only Root can create system-level users
    - Creator role must be higher than target role
    - Super Admin can only create users within their org
    
    Args:
        creator_role: Role of user making the change
        target_role: Role being assigned
    
    Returns: True if authorized, False otherwise
    """
    if not creator_role or target_role == "Root":
        return False
    
    if creator_role not in ROLE_HIERARCHY:
        return False
    
    try:
        creator_level = ROLE_HIERARCHY.index(creator_role)
        target_level = ROLE_HIERARCHY.index(target_role)
        return creator_level > target_level
    except (ValueError, IndexError):
        return False


# ============================================================
# USER CREATION & MANAGEMENT
# ============================================================

def create_user_validated(
    db: Session,
    user_data: Dict[str, Any],
    creator_id: str,
    creator_role: Optional[str] = None
) -> models.DBUser:
    """
    Create user with comprehensive validation and audit trail.
    
    Validation steps:
    1. Verify creator has authority
    2. Validate role hierarchy
    3. Check organization exists (if org-scoped)
    4. Validate uniqueness (username, Super Admin)
    5. Validate system user isolation
    6. Create audit log
    
    Args:
        db: Database session
        user_data: User data dict with username, password, role, organization_id, etc.
        creator_id: ID of user creating this user
        creator_role: Role of creator (auto-fetched if None)
    
    Returns: Created DBUser instance
    
    Raises: HTTPException with validation errors
    """
    # 1. DETERMINE CREATOR ROLE
    if creator_role is None:
        if creator_id == "root-system-001":  # In-memory Root
            creator_role = "Root"
        else:
            creator_user = db.query(models.DBUser).filter(
                models.DBUser.id == creator_id
            ).first()
            creator_role = creator_user.role if creator_user else None
    
    # 2. VALIDATE CREATOR AUTHORITY
    target_role = user_data.get("role", "User")
    
    if not validate_creator_authority(creator_role, target_role):
        raise HTTPException(
            status_code=403,
            detail=f"Role '{creator_role}' cannot create users with role '{target_role}'"
        )
    
    # 3. PREVENT ROOT CREATION
    if target_role == "Root":
        raise HTTPException(
            status_code=403,
            detail="Root user cannot be created through API"
        )
    
    # 4. ORGANIZATION VALIDATION
    org_id = user_data.get("organization_id")
    
    if target_role == "Super Admin":
        if not org_id:
            raise HTTPException(
                status_code=400,
                detail="Super Admin must be assigned to an organization"
            )
        
        org = validate_organization_exists(db, org_id)
        
        # Check uniqueness of Super Admin
        if not validate_super_admin_uniqueness(db, org_id):
            raise HTTPException(
                status_code=400,
                detail=f"Organization {org_id} already has a Super Admin"
            )
    
    elif org_id:
        validate_organization_exists(db, org_id)
    
    # 5. SYSTEM USER ISOLATION
    isolation_check = validate_system_user_isolation(user_data)
    if not isolation_check["valid"]:
        raise HTTPException(
            status_code=400,
            detail=isolation_check["errors"][0]
        )
    
    # 6. USERNAME UNIQUENESS
    username = user_data.get("username", "").strip().lower()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    
    existing_user = db.query(models.DBUser).filter(
        models.DBUser.username == username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail=f"Username '{username}' already exists"
        )
    
    # 7. EMAIL UNIQUENESS (if provided)
    email = user_data.get("email")
    if email:
        existing_email = db.query(models.DBUser).filter(
            models.DBUser.email == email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=409,
                detail=f"Email '{email}' already in use"
            )
    
    # 8. CREATE USER
    password = user_data.get("password")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    
    db_user = models.DBUser(
        id=user_data.get("id") or str(uuid.uuid4()),
        username=username,
        password_hash=get_password_hash(password),
        role=target_role,
        name=user_data.get("name"),
        email=email,
        organization_id=org_id,
        is_system_user=user_data.get("is_system_user", False),
        is_active=user_data.get("is_active", True),
        created_by=creator_id,
        updated_by=creator_id,
    )
    
    db.add(db_user)
    db.flush()  # Get ID before logging
    
    # 9. AUDIT LOG
    log_audit_event(
        db=db,
        user={"id": creator_id, "role": creator_role, "organization_id": org_id},
        action="USER_CREATED",
        status="success",
        details={
            "user_id": db_user.id,
            "username": username,
            "role": target_role,
            "organization_id": org_id
        }
    )
    
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User '{username}' (id={db_user.id}) created by {creator_id}")
    return db_user


def update_user_role(
    db: Session,
    user_id: str,
    new_role: str,
    updater_id: str,
    reason: Optional[str] = None
) -> models.DBUser:
    """
    Update user role with strict validation and comprehensive audit.
    
    Validation:
    1. User exists
    2. Updater has authority
    3. Cannot demote last Super Admin
    4. New role is valid
    
    Args:
        db: Database session
        user_id: ID of user to update
        new_role: New role to assign
        updater_id: ID of user making the change
        reason: Optional reason for change
    
    Returns: Updated DBUser instance
    
    Raises: HTTPException with validation errors
    """
    # 1. FETCH USERS
    target_user = db.query(models.DBUser).filter(
        models.DBUser.id == user_id
    ).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fetch updater
    if updater_id == "root-system-001":
        updater_role = "Root"
    else:
        updater = db.query(models.DBUser).filter(
            models.DBUser.id == updater_id
        ).first()
        updater_role = updater.role if updater else None
    
    # 2. VALIDATE AUTHORITY
    if not validate_creator_authority(updater_role, new_role):
        raise HTTPException(
            status_code=403,
            detail=f"Role '{updater_role}' cannot assign role '{new_role}'"
        )
    
    # 3. VALIDATE TARGET ROLE
    if new_role not in ROLE_HIERARCHY and new_role != "Root":
        raise HTTPException(status_code=400, detail=f"Invalid role '{new_role}'")
    
    # 4. PREVENT DEMOTING LAST SUPER ADMIN
    if target_user.role == "Super Admin" and new_role != "Super Admin":
        if target_user.organization_id:
            other_admins = db.query(models.DBUser).filter(
                models.DBUser.organization_id == target_user.organization_id,
                models.DBUser.role == "Super Admin",
                models.DBUser.id != user_id
            ).count()
            
            if other_admins == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot demote the only Super Admin of an organization"
                )
    
    # 5. PREVENT PROMOTING TO ROOT
    if new_role == "Root":
        raise HTTPException(
            status_code=403,
            detail="Users cannot be promoted to Root role"
        )
    
    # 6. UPDATE ROLE
    old_role = target_user.role
    target_user.role = new_role
    target_user.updated_by = updater_id
    target_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(target_user)
    
    # 7. AUDIT LOG
    log_audit_event(
        db=db,
        user={"id": updater_id, "role": updater_role, "organization_id": target_user.organization_id},
        action="ROLE_CHANGED",
        status="success",
        details={
            "user_id": user_id,
            "username": target_user.username,
            "old_role": old_role,
            "new_role": new_role,
            "reason": reason
        }
    )
    
    logger.info(f"User '{target_user.username}' role changed from '{old_role}' to '{new_role}' by {updater_id}")
    return target_user


def prevent_super_admin_deletion(db: Session, user_id: str) -> Optional[str]:
    """
    Check if user is the last Super Admin of their organization.
    
    Returns: Organization ID if user is last Super Admin, None otherwise
    """
    user = db.query(models.DBUser).filter(models.DBUser.id == user_id).first()
    
    if not user or user.role != "Super Admin" or not user.organization_id:
        return None
    
    other_admins = db.query(models.DBUser).filter(
        models.DBUser.organization_id == user.organization_id,
        models.DBUser.role == "Super Admin",
        models.DBUser.id != user_id
    ).count()
    
    if other_admins == 0:
        return user.organization_id  # Prevent deletion
    
    return None


# ============================================================
# PERMISSION MANAGEMENT
# ============================================================

def grant_permission(
    db: Session,
    role: str,
    permission: str,
    organization_id: Optional[str] = None,
    granter_id: Optional[str] = None
) -> models.DBRolePermission:
    """
    Grant permission to a role.
    
    Args:
        db: Database session
        role: Role to grant permission to
        permission: Permission name
        organization_id: Organization scope (None = system-wide)
        granter_id: User granting permission (for audit)
    
    Returns: Created DBRolePermission instance
    """
    # Check if already granted
    existing = db.query(models.DBRolePermission).filter(
        models.DBRolePermission.role == role,
        models.DBRolePermission.permission == permission,
        models.DBRolePermission.organization_id == organization_id
    ).first()
    
    if existing:
        return existing
    
    # Create new permission grant
    perm = models.DBRolePermission(
        id=str(uuid.uuid4()),
        role=role,
        permission=permission,
        organization_id=organization_id,
        created_by=granter_id,
        updated_by=granter_id,
    )
    
    db.add(perm)
    db.commit()
    db.refresh(perm)
    
    # Audit
    if granter_id:
        log_audit_event(
            db=db,
            user={"id": granter_id},
            action="PERMISSION_GRANTED",
            status="success",
            details={
                "role": role,
                "permission": permission,
                "organization_id": organization_id
            }
        )
    
    return perm


def revoke_permission(
    db: Session,
    role: str,
    permission: str,
    organization_id: Optional[str] = None,
    revoker_id: Optional[str] = None
) -> bool:
    """
    Revoke permission from a role.
    
    Args:
        db: Database session
        role: Role to revoke from
        permission: Permission name
        organization_id: Organization scope
        revoker_id: User revoking permission (for audit)
    
    Returns: True if revoked, False if didn't exist
    """
    perm = db.query(models.DBRolePermission).filter(
        models.DBRolePermission.role == role,
        models.DBRolePermission.permission == permission,
        models.DBRolePermission.organization_id == organization_id
    ).first()
    
    if not perm:
        return False
    
    db.delete(perm)
    db.commit()
    
    # Audit
    if revoker_id:
        log_audit_event(
            db=db,
            user={"id": revoker_id},
            action="PERMISSION_REVOKED",
            status="success",
            details={
                "role": role,
                "permission": permission,
                "organization_id": organization_id
            }
        )
    
    return True


# ============================================================
# QUERY FILTERS FOR ROOT/ORG VISIBILITY
# ============================================================

def filter_users_by_visibility(
    query,
    current_user: Dict[str, Any]
) -> Any:
    """
    Filter user query based on current user's visibility permissions.
    
    Rules:
    - Root: Sees all users
    - Super Admin: Sees users in own org + system users
    - Others: Sees users in own org only
    
    Args:
        query: SQLAlchemy query object
        current_user: Current user dictionary (from dependency)
    
    Returns: Filtered query
    """
    user_role = current_user.get("role")
    user_org = current_user.get("organization_id")
    
    if user_role == "Root":
        # Root sees all users
        return query
    
    elif user_role == "Super Admin":
        # Super Admin sees own org users + system users (but not Root)
        from sqlalchemy import or_
        return query.filter(
            or_(
                models.DBUser.organization_id == user_org,
                models.DBUser.is_system_user == True
            ),
            models.DBUser.role != "Root"
        )
    
    else:
        # Regular users see only own org
        return query.filter(
            models.DBUser.organization_id == user_org,
            models.DBUser.role != "Root"
        )


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def can_user_manage_role(
    current_user: Dict[str, Any],
    target_user: models.DBUser
) -> bool:
    """
    Check if current user can manage target user's role.
    
    Rules:
    - Root can manage anyone
    - Super Admin can manage anyone in their org
    - Others cannot manage anyone
    """
    current_role = current_user.get("role")
    current_org = current_user.get("organization_id")
    
    if current_role == "Root":
        return True
    
    if current_role == "Super Admin" and current_org == target_user.organization_id:
        return True
    
    return False


def list_superadmins_by_org(db: Session) -> Dict[str, models.DBUser]:
    """
    Get Super Admin for each organization.
    
    Returns: Dictionary mapping org_id -> Super Admin user
    """
    admins = db.query(models.DBUser).filter(
        models.DBUser.role == "Super Admin"
    ).all()
    
    return {admin.organization_id: admin for admin in admins}
