
import os
import datetime
from typing import Optional, List, Union
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWTError as JWTError
import bcrypt
from passlib.context import CryptContext

from backend.database import SessionLocal
from backend import schemas
from backend.config import settings, auth_config
from backend.permissions_config import DEFAULT_ROLE_PERMISSIONS, SUPER_ROLES, SYSTEM_ROOT_ROLES

# Logger
import logging
logger = logging.getLogger(__name__)

# Constants
SECRET_KEY = os.getenv("SECRET_KEY", "change_this_in_production_9s8d7f98s7d9f8s7")
ALGORITHM = "HS256"

# Role Hierarchy - Import from single source of truth
ORG_SETUP_ROLES = SUPER_ROLES | {"Business Admin"}

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password Utils
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    try:
        # Support both passlib hashes and raw bcrypt
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)
    except Exception:
        # Fallback to passlib if bcrypt fails (e.g. unknown format)
        return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")

# Token Utils
def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# In-Memory Root User (Never stored in database)
ROOT_USER_ID = "root-system-001"
ROOT_USERNAME = "root"
ROOT_PASSWORD = os.getenv("ROOT_PASSWORD", "root")  # Change in production via ROOT_PASSWORD env var
ROOT_ROLE = "Root"

def get_root_password_hash():
    """Get Root password hash - hardcoded for system initialization"""
    return get_password_hash(ROOT_PASSWORD)

# Current User Dependency
def get_current_user(
    request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Check if Root user (always available in-memory)
    if username == ROOT_USERNAME:
        user_dict = {
            "id": ROOT_USER_ID,
            "username": ROOT_USERNAME,
            "role": ROOT_ROLE,
            "organization_id": None,
            "status": "Active",
            "avatar": f"https://ui-avatars.com/api/?name={ROOT_USERNAME}&background=FF6B6B",
            "employeeId": None,
            # Root always has full system access
            "can_view_all_orgs": True,
        }
        logger.info(f"✓ Root user authenticated in-memory (no DB lookup)")
        return user_dict

    # All other users must exist in database
    from backend.domains.core.models import DBUser
    user = db.query(DBUser).filter(DBUser.username == username).first()
    if user is None:
        raise credentials_exception

    # Determine effective Organization ID and Root 'full-access' behavior
    # Default to the user's organization. Allow switching via `x-organization-id`
    # for Root and SystemAdmin. If Root does not provide a header, treat them
    # as having 'can_view_all_orgs' (FULL ACCESS mode) so core code can decide to
    # avoid organization filtering centrally.
    effective_org_id = user.organization_id
    header_org_id = request.headers.get("x-organization-id")

    # Allow only Root and SystemAdmin to switch contexts
    ALLOWED_SWITCH_ROLES = SUPER_ROLES | {"SystemAdmin"}

    if header_org_id and user.role in ALLOWED_SWITCH_ROLES:
        effective_org_id = header_org_id

    # Root without header gets full-access and can view across orgs
    # STRICT REDESIGN: Only SYSTEM_ROOT_ROLES (Root) get this capability. 
    # Super Admin (ORG_SUPER_ROLES) is strictly scoped.
    can_view_all_orgs = False
    if user.role in SYSTEM_ROOT_ROLES and not header_org_id:
        can_view_all_orgs = True

    # Construct dict for legacy compat (logic preserved from main.py)
    user_dict = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "organization_id": effective_org_id,
        "status": "Active" if user.is_active else "Inactive",
        "avatar": f"https://ui-avatars.com/api/?name={user.username}&background=random",
        "employeeId": user.employee_id,
        # Central flag: True when Root should see across all orgs
        "can_view_all_orgs": can_view_all_orgs,
    }
    return user_dict

def get_user_org(current_user: dict) -> Optional[str]:
    """
    Returns the organization ID for filtering.
    Returns None if the user is a Root user (system-wide access without organization scoping),
    signaling to the caller that organization filtering should be bypassed.
    """
    if current_user.get("can_view_all_orgs"):
        return None
    return current_user.get("organization_id")

def can_view_root_user(current_user: dict) -> bool:
    """
    Check if current user can view Root user.
    Rule: Only Root can see Root user and its permissions.
    All other users cannot see Root user in lists, details, or permissions.
    """
    return current_user.get("role") == "Root"

def log_audit_event(db: Session, user: dict, action: str, status: str = "Hashed", details: str = None):
    """Record an audit log for the current user action"""
    try:
        log_data = schemas.AuditLogCreate(
            organization_id=user.get("organization_id"),
            user=user.get("username", "Unknown"),
            action=action,
            status=status,
            time=datetime.datetime.now().isoformat(),
            details=details
        )
        from backend import crud
        crud.create_audit_log(db, log_data)
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")

# RBAC Dependencies
def requires_role(*allowed_roles):
    """RBAC Dependency: Ensures user has one of the allowed roles."""
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "")
        
        # Super roles bypass all checks
        if user_role in SUPER_ROLES:
            return current_user
            
        if user_role in allowed_roles:
            return current_user
            
        raise HTTPException(
            status_code=403,
            detail=f"Access Forbidden: Role '{user_role}' not in allowed roles {allowed_roles}",
        )
    return role_checker

def check_permission(permission: str):
    def permission_checker(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
        try:
            user_role = current_user.get("role", "")
            
            # 1. Super Admin / Root Bypass - Always has all permissions
            logger.info(f"CHECK_PERM: Role=[{user_role}] Needed=[{permission}] SUPER_ROLES={SUPER_ROLES}")
            if user_role in SUPER_ROLES:
                return current_user
                
            # 2. Check DB Permissions
            from backend import crud
            role_perms = crud.get_role_permissions(db, user_role)
            
            # 3. Fallback to Default Permissions if DB is empty
            if not role_perms:
                role_perms = DEFAULT_ROLE_PERMISSIONS.get(user_role, [])
            
            # 4. Check if permission exists in role permissions
            # Wildcard permission grants all access
            if '*' in role_perms or permission in role_perms:
                return current_user
                
            raise HTTPException(
                status_code=403,
                detail=f"Access Forbidden: Role '{user_role}' lacks permission '{permission}'",
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"SYSTEM ERROR in permission_checker: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))
    return permission_checker


# Convenience dependency for routers expecting an "active" user
def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Return the current user if active; raise 403 if inactive."""
    if current_user.get("status") != "Active":
        raise HTTPException(status_code=403, detail="User account is not active")
    return current_user
