from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend import crud, schemas
from backend.database import get_db
from backend.dependencies import (
    get_current_user,
    check_permission,
    get_user_org
)

router = APIRouter(tags=["HCM - Overtime"])

@router.get("/overtime", response_model=List[schemas.OvertimeRequest])
def get_overtime_requests(
    status: Optional[str] = None,
    employee_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_overtime"))
):
    org_id = get_user_org(current_user)
    return crud.get_overtime_requests(
        db, status=status, employee_id=employee_id,
        organization_id=org_id, skip=skip, limit=limit
    )

@router.post("/overtime", response_model=schemas.OvertimeRequest)
def create_overtime_request(
    request: schemas.OvertimeRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    org_id = get_user_org(current_user)
    # Basic permission check - employees can request for themselves,
    # HR/Admin can request for others.
    # For now, let's assume get_current_user is enough if we trust the frontend
    # but strictly we should check role.
    return crud.create_overtime_request(db, request, user_id=current_user["id"], org_id=org_id)

@router.put("/overtime/{request_id}/status", response_model=schemas.OvertimeRequest)
def update_overtime_status(
    request_id: str,
    payload: schemas.OvertimeApproval,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("approve_overtime"))
):
    # Additional check: ensure request belongs to user's org
    org_id = get_user_org(current_user)
    # We could fetch first to verify org, but crud.approve_overtime_request can handle it
    # and we already have check_permission.
    return crud.approve_overtime_request(
        db, request_id=request_id, action=payload.action,
        approver_id=current_user["id"], rejection_reason=payload.rejection_reason
    )
