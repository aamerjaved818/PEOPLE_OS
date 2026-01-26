from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend import crud, schemas
from backend.database import get_db
from backend.dependencies import (
    check_permission,
    get_user_org
)

router = APIRouter(tags=["HCM - Benefits"])

@router.get("/benefits/enrollments", response_model=List[schemas.BenefitEnrollment])
def get_enrollments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_benefit_enrollments(db, organization_id=org_id)

@router.get("/benefits/tiers", response_model=List[schemas.BenefitTier])
def get_tiers(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_benefit_tiers(db, organization_id=org_id)

@router.put("/benefits/enrollments/{enrollment_id}/tier", response_model=schemas.BenefitEnrollment)
def update_enrollment_tier(
    enrollment_id: str,
    tier: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    updated = crud.update_benefit_enrollment_tier(db, enrollment_id, tier)
    if not updated:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return updated

@router.post("/benefits/tiers", response_model=schemas.BenefitTier)
def create_tier(
    tier: schemas.BenefitTierCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    org_id = get_user_org(current_user)
    return crud.create_benefit_tier(db, tier, organization_id=org_id, user_id=current_user["id"])
