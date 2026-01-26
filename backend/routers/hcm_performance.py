from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend import crud, schemas
from backend.database import get_db
from backend.dependencies import (
    check_permission,
    get_user_org
)

router = APIRouter(tags=["HCM - Performance"])

@router.get("/performance/goals", response_model=List[schemas.Goal])
def get_goals(
    employee_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_goals(db, organization_id=org_id, employee_id=employee_id)

@router.post("/performance/goals", response_model=schemas.Goal)
def create_goal(
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    org_id = get_user_org(current_user)
    if org_id is not None and not goal.organization_id:
        goal.organization_id = org_id
    return crud.create_goal(db, goal, organization_id=org_id, user_id=current_user["id"])

@router.delete("/performance/goals/{goal_id}")
def delete_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    success = crud.delete_goal(db, goal_id=goal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"status": "success"}
