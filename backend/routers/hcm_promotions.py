from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend import schemas, crud
from backend.dependencies import check_permission, get_user_org

router = APIRouter(tags=["HCM Promotions"])

@router.get("/promotions/cycles", response_model=List[schemas.PromotionCycle])
def get_cycles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("manage_master_data"))
):
    org_id = get_user_org(current_user)
    return crud.get_promotion_cycles(db, organization_id=org_id)

@router.post("/promotions/cycles", response_model=schemas.PromotionCycle)
def create_cycle(
    cycle: schemas.PromotionCycleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("manage_master_data"))
):
    org_id = get_user_org(current_user)
    return crud.create_promotion_cycle(db, cycle=cycle, organization_id=org_id, user_id=current_user["id"])

@router.get("/promotions/requests", response_model=List[schemas.PromotionRequest])
def get_requests(
    employee_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_promotion_requests(db, organization_id=org_id, employee_id=employee_id)

@router.post("/promotions/requests", response_model=schemas.PromotionRequest)
def create_request(
    request: schemas.PromotionRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("manage_employees"))
):
    org_id = get_user_org(current_user)
    return crud.create_promotion_request(db, request=request, organization_id=org_id, user_id=current_user["id"])

@router.post("/promotions/approve", response_model=schemas.PromotionRequest)
def approve_request(
    approval: schemas.PromotionApprovalCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("manage_employees"))
):
    # Additional logic to verify role level (HR/Finance/Final) could be added here
    return crud.approve_promotion_request(db, approval=approval, user_id=current_user["id"])
