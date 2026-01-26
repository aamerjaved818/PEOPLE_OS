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

router = APIRouter(tags=["HCM - Onboarding"])

@router.get("/onboarding/hires", response_model=List[schemas.OnboardingHire])
def get_onboarding_hires(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_onboarding_hires(db, organization_id=org_id)

@router.post("/onboarding/hires", response_model=schemas.OnboardingHire)
def create_onboarding_hire(
    hire: schemas.OnboardingHireCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    org_id = get_user_org(current_user)
    if org_id is not None and not hire.organization_id:
        hire.organization_id = org_id
    return crud.create_onboarding_hire(db, hire, organization_id=org_id, user_id=current_user["id"])

@router.put("/onboarding/hires/{hire_id}/steps/{step_id}", response_model=schemas.OnboardingHire)
def toggle_onboarding_step(
    hire_id: str,
    step_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    updated = crud.update_onboarding_step(db, hire_id=hire_id, step_id=step_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Step or Hire not found")
    return updated
