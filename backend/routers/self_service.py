from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from backend import crud, schemas, models
from backend.database import get_db
from backend.dependencies import (
    get_current_user,
    check_permission,
    get_user_org
)
from backend.services.file_upload import file_upload_service

router = APIRouter(prefix="/self-service", tags=["Self-Service"])

@router.get("/profile", response_model=schemas.MyProfile)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    emp_id = current_user.get("employeeId") or current_user.get("employee_id")
    if not emp_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud.get_my_profile(db, employee_id=emp_id)

@router.put("/profile")
def update_my_profile(
    profile_data: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    emp_id = current_user.get("employeeId") or current_user.get("employee_id")
    if not emp_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud.update_my_profile(db, employee_id=emp_id, profile_data=profile_data)

@router.get("/payslips")
def get_my_payslips(
    year: int = None,
    month: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    emp_id = current_user.get("employeeId") or current_user.get("employee_id")
    if not emp_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud.get_my_payslips(db, employee_id=emp_id, year=year, month=month, skip=skip, limit=limit)

@router.get("/team-directory", response_model=List[schemas.TeamMember])
def get_team_directory(
    department_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    org_id = get_user_org(current_user)
    return crud.get_team_directory(db, organization_id=org_id, department_id=department_id, skip=skip, limit=limit)

@router.post("/document-requests", response_model=schemas.DocumentRequest)
def create_document_request(
    request_data: schemas.DocumentRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    emp_id = current_user.get("employeeId") or current_user.get("employee_id")
    if not emp_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud.create_document_request(db, request_data, employee_id=emp_id)

@router.get("/notifications", tags=["Notifications"])
def get_my_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    from backend.services.notification_service import notification_service
    emp_id = current_user.get("employeeId") or current_user.get("employee_id")
    if not emp_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    return notification_service.get_my_notifications(
        db, employee_id=emp_id, unread_only=unread_only, limit=limit
    )
