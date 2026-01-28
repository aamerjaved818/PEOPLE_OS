from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import datetime
import shutil
import os
import uuid

from backend import crud, schemas, models
from backend.database import get_db
from backend.dependencies import (
    get_current_user,
    requires_role,
    get_user_org
)
from backend.config import settings

router = APIRouter(tags=["System"])



@router.get("/system/flags", response_model=schemas.SystemFlags)
def read_system_flags(db: Session = Depends(get_db), current_user: dict = Depends(requires_role("SystemAdmin"))):
    org_id = current_user.get("organization_id")
    
    # System admins (Root) without org_id should use the first organization or return defaults
    if not org_id:
        # Try to get any organization, or use a system org ID
        from sqlalchemy import func
        org = db.query(models.DBOrganization).first()
        if org:
            org_id = org.id
        else:
            # No organizations exist, return default flags
            return {
                "id": "system-default",
                "organization_id": None,
                "backup_retention_days": 30,
                "enable_audit_log": True,
                "enable_two_factor": False,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now(),
            }
    
    flags = crud.get_system_flags(db, org_id)
    if not flags:
        # Return default flags if none exist
        return {
            "id": "system-default",
            "organization_id": org_id,
            "backup_retention_days": 30,
            "enable_audit_log": True,
            "enable_two_factor": False,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
        }
    return flags

@router.post("/system/audit/run")
async def run_audit_endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(requires_role("SystemAdmin"))
):
    from backend.audit.audit_engine import run_system_audit
    report = run_system_audit(executed_by=current_user["id"])
    return {"status": "success", "report_id": report.id, "overall_score": report.overall_score}

@router.post("/system/maintenance/backups")
def create_backup(current_user: dict = Depends(requires_role("SystemAdmin"))):
    try:
        current_db = settings.DB_PATH
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"people_os.db.bak_{timestamp}"
        data_dir = os.path.dirname(current_db)
        backup_path = os.path.join(data_dir, backup_filename)
        shutil.copy2(current_db, backup_path)
        return {"status": "success", "filename": backup_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/api-keys", response_model=schemas.ApiKeyList)
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: dict = Depends(requires_role("SystemAdmin"))
):
    org_id = get_user_org(current_user)
    keys = crud.get_api_keys(db, org_id)
    return {"keys": keys, "total": len(keys)}

@router.get("/system/logs")
def get_system_logs(
    lines: int = 100,
    current_user: dict = Depends(requires_role("SystemAdmin"))
):
    """
    Retrieve the last N lines of the system log file.
    Restricted to SystemAdmin.
    """
    try:
        from backend.config import settings
        # Resolve log path (must match logging_config.py logic)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_file = os.path.join(project_root, "logs", "people_os.log")
        
        if not os.path.exists(log_file):
            return {"logs": ["Log file not found."], "path": log_file}

        # Read last N lines efficiently
        with open(log_file, "r", encoding="utf-8") as f:
            # Simple approach for reasonable usage
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]
            
        return {"logs": [line.strip() for line in last_lines], "total": len(all_lines), "shown": len(last_lines)}
    except Exception as e:
        return {"logs": [f"Error reading logs: {str(e)}"], "error": True}

@router.get("/audit/history", tags=["System Audit"])
def get_audit_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(requires_role("Root", "SystemAdmin"))
):
    """Placeholder for audit history."""
    return []

@router.get("/audit/regressions", tags=["System Audit"])
def get_audit_regressions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(requires_role("Root", "SystemAdmin"))
):
    """Placeholder for audit regressions."""
    return []

@router.get("/audit-logs", tags=["System Audit"])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(requires_role("Root", "SystemAdmin"))
):
    """Placeholder for audit logs."""
    return []

@router.get("/system/initial-data", response_model=schemas.InitialData)
def get_initial_data(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    org_id = get_user_org(current_user)
    return crud.get_initial_data(db, organization_id=org_id, current_user=current_user)
