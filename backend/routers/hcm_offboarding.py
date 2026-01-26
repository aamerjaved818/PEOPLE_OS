from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import crud, schemas, models
from backend.database import get_db
from backend.dependencies import (
    get_current_user,
    check_permission,
    get_user_org
)

router = APIRouter(tags=["HCM - Offboarding"])

@router.get("/offboarding/exits", response_model=List[schemas.OffboardingExit])
def get_offboarding_exits(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_offboarding_exits(db, organization_id=org_id)

@router.post("/offboarding/exits", response_model=schemas.OffboardingExit)
def create_offboarding_exit(
    exit: schemas.OffboardingExitCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    org_id = get_user_org(current_user)
    if org_id is not None and not exit.organization_id:
        exit.organization_id = org_id
    return crud.create_offboarding_exit(db, exit, organization_id=org_id, user_id=current_user["id"])

@router.put("/offboarding/exits/{exit_id}/checklist/{item_id}", response_model=schemas.OffboardingExit)
def update_offboarding_checklist(
    exit_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    updated = crud.update_offboarding_checklist(db, exit_id=exit_id, item_id=item_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Exit or Step not found")
    return updated
