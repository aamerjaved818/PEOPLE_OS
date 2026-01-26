from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from backend import crud, schemas
from backend.database import get_db
from backend.shared.models import models
from backend.dependencies import (
    get_current_user,
    check_permission,
    get_user_org
)
from backend.services import tax_calculator

router = APIRouter(tags=["HCM - Payroll"])

@router.get("/payroll", response_model=List[schemas.PayrollLedger])
def get_payroll_records(
    employee_id: Optional[str] = None,
    period_month: Optional[str] = None,
    period_year: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_payroll"))
):
    # Added critical check_permission("view_payroll")
    return crud.get_payroll_records(
        db, employee_id=employee_id, period_month=period_month,
        period_year=period_year, skip=skip, limit=limit
    )

@router.post("/payroll/generate")
def generate_payroll(
    request: schemas.PayrollGenerateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("manage_payroll"))
):
    # Added critical check_permission("manage_payroll")
    records = crud.generate_monthly_payroll(
        db, request.period_month, request.period_year,
        user_id=current_user["id"]
    )
    return {"generated": len(records), "period": f"{request.period_month} {request.period_year}"}

@router.get("/payroll/components", response_model=List[schemas.SalaryComponent])
def get_salary_components(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_payroll"))
):
    org_id = get_user_org(current_user)
    return crud.get_salary_components(db, organization_id=org_id, active_only=active_only)

@router.post("/payroll/components", response_model=schemas.SalaryComponent)
def create_salary_component(
    component: schemas.SalaryComponentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("manage_payroll"))
):
    return crud.create_salary_component(db, component, user_id=current_user["id"])

@router.get("/payroll/tax-slabs", response_model=List[schemas.TaxSlab])
def get_tax_slabs(
    tax_year: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_payroll"))
):
    org_id = get_user_org(current_user)
    return crud.get_tax_slabs(db, organization_id=org_id, tax_year=tax_year)

@router.post("/payroll/tax-slabs", response_model=schemas.TaxSlab)
def create_tax_slab(
    slab: schemas.TaxSlabCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("manage_payroll"))
):
    return crud.create_tax_slab(db, slab, user_id=current_user["id"])

@router.get("/payroll/runs", response_model=List[schemas.PayrollRun])
def get_payroll_runs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_payroll"))
):
    org_id = get_user_org(current_user)
    return crud.get_payroll_runs(db, organization_id=org_id, skip=skip, limit=limit)

@router.post("/payroll/runs/process", response_model=schemas.PayrollRun)
def process_payroll_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("manage_payroll"))
):
    return crud.process_payroll_run(db, run_id, user_id=current_user["id"])

@router.get("/tax-calculation/{employee_id}/{tax_year}", response_model=schemas.TaxCalculationDetail)
def get_tax_calculation(
    employee_id: str,
    tax_year: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_payroll"))
):
    try:
        return tax_calculator.calculate_employee_tax(db, employee_id, tax_year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Payroll Settings
@router.get("/payroll-settings", response_model=schemas.PayrollSettings)
def get_payroll_settings(db: Session = Depends(get_db), current_user: dict = Depends(check_permission("view_payroll"))):
    org_id = current_user.get("organization_id")
    
    # If user is system admin without org, use the first organization
    if not org_id:
        org = db.query(models.DBOrganization).first()
        if org:
            org_id = org.id
        else:
            # Return default settings if no organizations exist
            return {
                "id": "default",
                "organization_id": None,
                "calculation_method": "Per Month",
                "custom_formulas": '{"staff": "", "worker": ""}',
                "overtime_rules": "{}",
                "currency": "PKR",
                "tax_year_start": "July",
                "allow_negative_salary": False,
                "pay_frequency": "Monthly",
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now(),
            }
    
    return crud.get_payroll_settings(db, organization_id=org_id)

@router.post("/payroll-settings")
def save_payroll_settings(settings: schemas.PayrollSettingsCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_payroll"))):
    return crud.save_payroll_settings(db, settings, organization_id=current_user.get("organization_id"), user_id=current_user["id"])
