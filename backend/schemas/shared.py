
import json
from datetime import datetime
from typing import Any, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class AuditBase(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

class ResultBase(BaseModel):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Any] = None

class AuditLogBase(BaseModel):
    user: str
    action: str
    status: str
    time: str
    details: Optional[str] = None
    organization_id: Optional[str] = Field(None, alias="organizationId")

    class Config:
        populate_by_name = True

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: str

    class Config:
        from_attributes = True
