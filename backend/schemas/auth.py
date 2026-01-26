
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from .shared import AuditBase

class LoginRequest(BaseModel):
    username: str
    password: str

# ===== API Key Schemas =====
class ApiKeyBase(BaseModel):
    name: str
    expires_at: Optional[datetime] = None

class ApiKeyCreate(ApiKeyBase):
    pass

class ApiKeyResponse(ApiKeyBase, AuditBase):
    id: str
    organization_id: str
    key_preview: str  # First 8 + last 4 chars of the key
    last_used: Optional[datetime] = None
    revoked: bool = False

    class Config:
        from_attributes = True

class ApiKeyCreateResponse(ApiKeyResponse):
    """Returned only at creation time with the full key"""
    raw_key: str

class ApiKeyList(BaseModel):
    """List of API keys (masked)"""
    keys: List[ApiKeyResponse]
    total: int

# ===== RBAC Schemas =====
class RolePermission(BaseModel):
    role: str
    permission: str

    class Config:
        from_attributes = True

class RolePermissionCreate(BaseModel):
    role: str
    permissions: List[str]

# ===== User Response Schema (Standardized) =====
class User(BaseModel):
    id: str
    username: str
    role: str
    organization_id: Optional[str] = None
    employee_id: Optional[str] = None
    is_active: bool = True
    is_system_user: bool = False

    class Config:
        from_attributes = True
