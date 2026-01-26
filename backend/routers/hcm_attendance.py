from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend import crud, schemas, models
from backend.database import get_db
from backend.dependencies import (
    get_current_user,
    check_permission,
    requires_role,
    get_user_org
)

router = APIRouter(tags=["HCM - Attendance"])

@router.get("/attendance", response_model=List[schemas.Attendance])
def get_attendance_records(
    employee_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_attendance"))
):
    org_id = current_user.get("organization_id")
    if employee_id:
        emp = db.query(models.DBEmployee).filter(
            models.DBEmployee.id == employee_id,
            models.DBEmployee.organization_id == org_id
        ).first()
        if not emp:
            raise HTTPException(403, "Access forbidden")
    
    return crud.get_attendance_records(
        db, employee_id=employee_id, date_from=date_from,
        date_to=date_to, organization_id=org_id, skip=skip, limit=limit
    )

@router.post("/attendance", response_model=schemas.Attendance)
def create_attendance(
    attendance: schemas.AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_attendance"))
):
    org_id = current_user.get("organization_id")
    return crud.create_attendance_record(db, attendance, user_id=current_user["id"], org_id=org_id)

@router.post("/attendance/bulk")
def bulk_create_attendance(
    payload: schemas.AttendanceBulkCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_attendance"))
):
    # Added critical check_permission("edit_attendance")
    return crud.bulk_create_attendance(db, payload.records, user_id=current_user["id"])

@router.post("/attendance/validate-bulk", response_model=schemas.AttendanceBulkValidationResponse)
def validate_bulk_attendance(
    request: schemas.AttendanceBulkValidationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_attendance"))
):
    # Added critical check_permission("edit_attendance")
    org_id = current_user.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=403, detail="Organization context required")
    
    return crud.validate_bulk_attendance_records(db, org_id, request.records, dry_run=request.dry_run)

@router.get("/attendance/search", response_model=schemas.AttendanceSearchResponse)
def search_attendance(
    employee_id: Optional[str] = None,
    employee_name: Optional[str] = None,
    department_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    status: Optional[str] = None,
    shift_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_attendance"))
):
    org_id = get_user_org(current_user)
    search_criteria = schemas.AttendanceSearch(
        employee_id=employee_id, employee_name=employee_name,
        department_id=department_id, date_from=date_from,
        date_to=date_to, status=status, shift_id=shift_id,
        skip=skip, limit=limit
    )
    records, total = crud.search_attendance_records(db, org_id, search_criteria)
    # Mapping logic omitted for brevity, assuming crud handles it or using a helper
    return {"total": total, "records": records, "skip": skip, "limit": limit}

@router.post("/attendance/corrections", response_model=schemas.AttendanceCorrection)
def create_attendance_correction(
    correction: schemas.AttendanceCorrectionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return crud.create_attendance_correction(db, correction, user_id=current_user["id"])

@router.put("/attendance/corrections/{correction_id}/status", response_model=schemas.AttendanceCorrection)
def update_correction_status(
    correction_id: str,
    payload: schemas.AttendanceCorrectionApproval,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("approve_attendance_corrections"))
):
    # Added specific permission check
    return crud.approve_attendance_correction(
        db, correction_id=correction_id, action=payload.action, 
        approver_id=current_user["id"], rejection_reason=payload.rejection_reason
    )
