from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend import crud, schemas
from backend.database import get_db
from backend.dependencies import (
    check_permission,
    get_user_org
)

router = APIRouter(tags=["HCM - Rewards"])

@router.get("/rewards", response_model=List[schemas.Reward])
def get_rewards(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_rewards(db, organization_id=org_id)

@router.get("/rewards/recognitions", response_model=List[schemas.Recognition])
def get_recognitions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_recognitions(db, organization_id=org_id)

@router.get("/rewards/points/{employee_id}", response_model=Optional[schemas.RewardPoint])
def get_points(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_reward_point_balance(db, employee_id=employee_id, organization_id=org_id)

@router.get("/rewards/points/{employee_id}/transactions", response_model=List[schemas.RewardPointTransaction])
def get_point_transactions(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_reward_point_transactions(db, employee_id=employee_id, organization_id=org_id)

@router.post("/rewards/recognitions", response_model=schemas.Recognition)
def create_recognition(
    recognition: schemas.RecognitionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    org_id = get_user_org(current_user)
    return crud.create_recognition(db, recognition, organization_id=org_id, user_id=current_user["id"])

@router.post("/rewards/redeem/{reward_id}", response_model=bool)
def redeem_reward(
    reward_id: int,
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    org_id = get_user_org(current_user)
    success = crud.redeem_reward(db, employee_id=employee_id, reward_id=reward_id, organization_id=org_id)
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient points or invalid reward")
    return success

@router.post("/rewards", response_model=schemas.Reward)
def create_reward(
    reward: schemas.RewardCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("admin_access"))
):
    org_id = get_user_org(current_user)
    return crud.create_reward(db, reward, organization_id=org_id, user_id=current_user["id"])
