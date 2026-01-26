from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import crud, schemas, models
from backend.database import get_db
from backend.dependencies import (
    get_current_user,
    requires_role,
    check_permission,
    get_user_org
)

router = APIRouter(tags=["Core Organization"])

@router.get("/organizations", response_model=List[schemas.OrganizationList])
def get_organizations(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Get organizations based on user role.
    
    - Root: Can view ALL organizations (system-wide access)
    - Super Admin / Business Admin: Can only view their assigned organization
    - Other roles: Can only view their assigned organization
    
    CRITICAL: Only Root has system-wide access. All others are org-scoped.
    """
    user_role = current_user.get("role", "")
    
    # ONLY ROOT has system-wide access to all organizations
    if user_role == "Root":
        return crud.get_organizations(db)
    
    # All other roles (including Super Admin, Business Admin, etc.) are org-scoped
    org_id = get_user_org(current_user)
    if org_id:
        org = crud.get_organization(db, org_id)
        return [org] if org else []
    
    # If no org assigned, return empty list (user has no access)
    return []

@router.get("/organizations/{org_id}", response_model=schemas.Organization)
def get_organization(
    org_id: str, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(requires_role("SystemAdmin", "Business Admin"))
):
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.post("/organizations", response_model=schemas.Organization)
def create_organization(
    org: schemas.OrganizationWithAdminCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(requires_role("Root"))
):
    return crud.create_organization(db, org, user_id=current_user["id"])

@router.put("/organizations/{org_id}", response_model=schemas.Organization)
def update_organization(
    org_id: str, 
    org: schemas.OrganizationCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(requires_role("SystemAdmin", "Business Admin"))
):
    return crud.update_organization(db, org_id, org, user_id=current_user["id"])

@router.delete("/organizations/{org_id}", tags=["System"])
def delete_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(requires_role("Root")),
):
    return crud.delete_organization(db, org_id, current_user_id=current_user.get("id"))

# Plants
@router.get("/plants", response_model=List[schemas.Plant])
def get_plants(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    org_id = get_user_org(current_user)
    return crud.get_plants(db, organization_id=org_id)

@router.post("/plants", response_model=schemas.Plant)
def create_plant(
    plant: schemas.PlantCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(check_permission("manage_org_structure"))
):
    if not plant.organization_id:
        plant.organization_id = current_user.get("organization_id")
    return crud.create_plant(db, plant, user_id=current_user["id"])

@router.put("/plants/{plant_id}", response_model=schemas.Plant)
def update_plant(
    plant_id: str, 
    plant: schemas.PlantCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(check_permission("manage_org_structure"))
):
    if not plant.organization_id:
        plant.organization_id = current_user.get("organization_id")
    return crud.update_plant(db, plant_id, plant, user_id=current_user["id"])

@router.delete("/plants/{plant_id}")
async def delete_plant(
    plant_id: str, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(check_permission("manage_org_structure"))
):
    if crud.delete_plant(db, plant_id):
        return {"message": "Plant deleted successfully"}
    raise HTTPException(status_code=404, detail="Plant not found")

# Departments
@router.get("/departments", response_model=List[schemas.Department])
def get_departments(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    org_id = get_user_org(current_user)
    return crud.get_departments(db, organization_id=org_id)

@router.post("/departments", response_model=schemas.Department)
def create_department(dept: schemas.DepartmentCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    if not dept.organization_id:
        dept.organization_id = current_user.get("organization_id")
    return crud.create_department(db, dept, user_id=current_user["id"])

@router.put("/departments/{dept_id}", response_model=schemas.Department)
def update_department(dept_id: str, dept: schemas.DepartmentCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    if not dept.organization_id:
        dept.organization_id = current_user.get("organization_id")
    return crud.update_department(db, dept_id, dept, user_id=current_user["id"])

@router.delete("/departments/{dept_id}")
def delete_department(dept_id: str, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    crud.delete_department(db, dept_id)
    return {"status": "success", "message": "Department deleted"}

# Grades
@router.get("/grades", response_model=List[schemas.Grade])
def get_grades(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    org_id = get_user_org(current_user)
    return crud.get_grades(db, organization_id=org_id)

@router.post("/grades", response_model=schemas.Grade)
def create_grade(grade: schemas.GradeCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    if not grade.organization_id:
        grade.organization_id = current_user.get("organization_id")
    return crud.create_grade(db, grade, user_id=current_user["id"])

# Designations
@router.get("/designations", response_model=List[schemas.Designation])
def get_designations(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    org_id = get_user_org(current_user)
    return crud.get_designations(db, organization_id=org_id)

@router.post("/designations", response_model=schemas.Designation)
def create_designation(desig: schemas.DesignationCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    return crud.create_designation(db, desig, user_id=current_user["id"], org_id=current_user.get("organization_id"))

# Job Levels
@router.get("/job-levels", response_model=List[schemas.JobLevel])
def get_job_levels(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    org_id = get_user_org(current_user)
    return crud.get_job_levels(db, organization_id=org_id)

@router.post("/job-levels", response_model=schemas.JobLevel)
def create_job_level(level: schemas.JobLevelCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    if not level.organization_id:
        level.organization_id = current_user.get("organization_id")
    return crud.create_job_level(db, level, user_id=current_user["id"])

# Holidays
@router.get("/holidays", response_model=List[schemas.Holiday])
def get_holidays(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    org_id = get_user_org(current_user)
    return crud.get_holidays(db, organization_id=org_id)

@router.post("/holidays", response_model=schemas.Holiday)
def create_holiday(holiday: schemas.HolidayCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    return crud.create_holiday(db, holiday, user_id=current_user["id"])

@router.put("/holidays/{holiday_id}", response_model=schemas.Holiday)
def update_holiday(holiday_id: str, holiday: schemas.HolidayCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    return crud.update_holiday(db, holiday_id, holiday, user_id=current_user["id"])

@router.delete("/holidays/{holiday_id}")
def delete_holiday(holiday_id: str, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    crud.delete_holiday(db, holiday_id)
    return {"status": "success"}

# Banks
@router.get("/banks", response_model=List[schemas.Bank])
def get_banks(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    org_id = get_user_org(current_user)
    return crud.get_banks(db, organization_id=org_id)

@router.post("/banks", response_model=schemas.Bank)
def create_bank(bank: schemas.BankCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    return crud.create_bank(db, bank, user_id=current_user["id"])

# Shifts
@router.get("/shifts", response_model=List[schemas.Shift])
def get_shifts(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    org_id = get_user_org(current_user)
    return crud.get_shifts(db, organization_id=org_id)

@router.post("/shifts", response_model=schemas.Shift)
def create_shift(shift: schemas.ShiftCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    return crud.create_shift(db, shift, user_id=current_user["id"])

# Sub-Departments
@router.get("/sub-departments", response_model=List[schemas.SubDepartment])
def get_sub_departments(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    org_id = get_user_org(current_user)
    return crud.get_sub_departments(db, organization_id=org_id)

@router.post("/sub-departments", response_model=schemas.SubDepartment)
def create_sub_department(sub: schemas.SubDepartmentCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    if not sub.organization_id:
        sub.organization_id = current_user.get("organization_id")
    return crud.create_sub_department(db, sub, user_id=current_user["id"])

@router.put("/sub-departments/{sub_id}", response_model=schemas.SubDepartment)
def update_sub_department(sub_id: str, sub: schemas.SubDepartmentCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    if not sub.organization_id:
        sub.organization_id = current_user.get("organization_id")
    return crud.update_sub_department(db, sub_id, sub, user_id=current_user["id"])

@router.delete("/sub-departments/{sub_id}")
def delete_sub_department(sub_id: str, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    crud.delete_sub_department(db, sub_id)
    return {"status": "success", "message": "Sub-department deleted"}

# Positions
@router.get("/positions", response_model=List[schemas.Position])
def get_positions(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    org_id = get_user_org(current_user)
    return crud.get_positions(db, organization_id=org_id)

@router.post("/positions", response_model=schemas.Position)
def create_position(pos: schemas.PositionCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    if not pos.organization_id:
        pos.organization_id = current_user.get("organization_id")
    return crud.create_position(db, pos, user_id=current_user["id"])

@router.put("/positions/{pos_id}", response_model=schemas.Position)
def update_position(pos_id: str, pos: schemas.PositionCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    if not pos.organization_id:
        pos.organization_id = current_user.get("organization_id")
    return crud.update_position(db, pos_id, pos, user_id=current_user["id"])

@router.delete("/positions/{pos_id}")
def delete_position(pos_id: str, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    crud.delete_position(db, pos_id)
    return {"status": "success", "message": "Position deleted"}

# Employment Levels
@router.get("/employment-levels", response_model=List[schemas.EmploymentLevel])
def get_employment_levels(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    org_id = get_user_org(current_user)
    return crud.get_employment_levels(db, organization_id=org_id)

@router.post("/employment-levels", response_model=schemas.EmploymentLevel)
def create_employment_level(level: schemas.EmploymentLevelCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    if not level.organization_id:
        level.organization_id = current_user.get("organization_id")
    return crud.create_employment_level(db, level, user_id=current_user["id"])

@router.put("/employment-levels/{level_id}", response_model=schemas.EmploymentLevel)
def update_employment_level(level_id: str, level: schemas.EmploymentLevelCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    if not level.organization_id:
        level.organization_id = current_user.get("organization_id")
    return crud.update_employment_level(db, level_id, level, user_id=current_user["id"])

@router.delete("/employment-levels/{level_id}")
def delete_employment_level(level_id: str, db: Session = Depends(get_db), current_user: dict = Depends(check_permission("manage_org_structure"))):
    crud.delete_employment_level(db, level_id)
    return {"status": "success", "message": "Employment level deleted"}
