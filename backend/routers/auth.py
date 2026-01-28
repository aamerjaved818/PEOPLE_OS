from backend.logging_config import logger
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend import crud, schemas, models
from backend.database import get_db
from backend.dependencies import (
    get_current_user,
    requires_role,
    check_permission,
    verify_password,
    create_access_token,
    log_audit_event,
    ROOT_USERNAME,
    ROOT_PASSWORD,
    ROOT_USER_ID,
    ROOT_ROLE,
    AMER_USERNAME,
    AMER_PASSWORD,
    AMER_USER_ID,
    AMER_ROLE
)
from backend.config import auth_config

router = APIRouter(tags=["Authentication & Users"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/rbac/permissions", response_model=List[schemas.RolePermission])
def get_role_permissions(
    role: str = None, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(requires_role("Root", "SystemAdmin"))
):
    return crud.get_role_permissions_list(db, role, current_user=current_user)

@router.post("/rbac/permissions")
def update_role_permissions(
    payload: schemas.RolePermissionCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(requires_role("Root", "SystemAdmin"))
):
    return crud.update_role_permissions(db, payload.role, payload.permissions)

@router.post("/auth/login", tags=["Authentication"])
@limiter.limit(auth_config.LOGIN_RATE_LIMIT)
def login(login_data: schemas.LoginRequest, request: Request, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {login_data.username}")
    
    # Check if Root user (in-memory, no DB lookup)
    if login_data.username == ROOT_USERNAME:
        if login_data.password == ROOT_PASSWORD:
            logger.info(f"[PASS] Root user authenticated successfully")
            access_token = create_access_token(data={
                "sub": ROOT_USERNAME, 
                "role": ROOT_ROLE, 
                "organization_id": None
            })
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": ROOT_USER_ID,
                    "username": ROOT_USERNAME,
                    "role": ROOT_ROLE,
                    "organizationId": None,
                    "employeeId": None,
                    "isSystemUser": True
                }
            }
        else:
            logger.warning(f"Invalid password for root user")
            raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if Amer user (secondary in-memory system user)
    if login_data.username == AMER_USERNAME:
        if login_data.password == AMER_PASSWORD:
            logger.info(f"[PASS] Amer user authenticated successfully")
            access_token = create_access_token(data={
                "sub": AMER_USERNAME, 
                "role": AMER_ROLE, 
                "organization_id": None
            })
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": AMER_USER_ID,
                    "username": AMER_USERNAME,
                    "role": AMER_ROLE,
                    "organizationId": None,
                    "employeeId": None,
                    "isSystemUser": True
                }
            }
        else:
            logger.warning(f"Invalid password for amer user")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # All other users must exist in database
    from sqlalchemy import func
    user = db.query(models.DBUser).filter(func.lower(models.DBUser.username) == login_data.username.lower()).first()
    if not user:
        logger.warning(f"User not found: {login_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(login_data.password, user.password_hash):
        logger.warning(f"Invalid password for user: {login_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=403, detail="User account is not active")
    
    access_token = create_access_token(data={
        "sub": user.username, 
        "role": user.role, 
        "organization_id": user.organization_id
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "organizationId": user.organization_id,
            "employeeId": user.employee_id,
            "isSystemUser": getattr(user, "is_system_user", False)
        }
    }

@router.get("/users", response_model=List[schemas.User], tags=["Users"])
def get_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(requires_role("SystemAdmin"))
):
    return crud.get_users(db, current_user=current_user)

@router.post("/users", response_model=schemas.User, tags=["Users"])
def create_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(requires_role("SystemAdmin"))
):
    try:
        return crud.create_user(db=db, user=user, creator_id=current_user["id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(
    user_id: str, 
    user: schemas.UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(check_permission("edit_users"))
):
    try:
        updated = crud.update_user(db, user_id, user, updater_id=current_user["id"])
        if not updated:
            raise HTTPException(404, "User not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/users/{user_id}", tags=["Users"])
def delete_user(
    user_id: str, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(requires_role("Root", "SystemAdmin"))
):
    try:
        return crud.delete_user(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
