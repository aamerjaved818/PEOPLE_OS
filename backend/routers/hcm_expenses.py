from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend import crud, schemas
from backend.database import get_db
from backend.dependencies import (
    check_permission,
    get_user_org
)

router = APIRouter(tags=["HCM - Expenses"])

@router.get("/expenses", response_model=List[schemas.Expense])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_expenses(db, organization_id=org_id)

@router.post("/expenses", response_model=schemas.Expense)
def save_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    org_id = get_user_org(current_user)
    return crud.save_expense(db, expense, organization_id=org_id, user_id=current_user["id"])
