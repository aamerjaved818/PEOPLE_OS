import logging
logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io

from backend import crud, schemas, models
from backend.database import get_db
from backend.dependencies import (
    get_current_user,
    check_permission,
    requires_role,
    get_user_org
)

router = APIRouter(tags=["HCM - Employees"])

@router.get("/employees")
def get_employees(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    query = db.query(models.DBEmployee)
    if org_id:
        query = query.filter(models.DBEmployee.organization_id == org_id)
    results = query.offset(skip).limit(limit).all()
    
    output = []
    for e in results:
        try:
            # Debug: log types/values of problematic fields before validation
            # Temporary debug log removed
            # Try to validate via schema
            validated = schemas.Employee.model_validate(e)
            output.append(validated.model_dump())
        except Exception as err:
            logger.error(f"VALIDATION FAILED for employee {e.id}: {err}")
            output.append({"id": e.id, "name": e.name, "SERIALIZATION_ERROR": str(err)})
    return output

@router.post("/employees", response_model=schemas.Employee)
def create_employee(
    employee: schemas.EmployeeCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(check_permission("edit_employee"))
):
    org_id = get_user_org(current_user)
    if org_id is not None and not employee.organization_id:
        employee.organization_id = org_id
    return crud.create_employee(db, employee, user_id=current_user["id"])

@router.get("/employees/search")
def search_employees(
    search: Optional[str] = None,
    department_id: Optional[str] = None,
    status: Optional[str] = None,
    plant_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    from sqlalchemy import or_
    org_id = get_user_org(current_user)
    if org_id is None:
        query = db.query(models.DBEmployee)
    else:
        query = db.query(models.DBEmployee).filter(models.DBEmployee.organization_id == org_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.DBEmployee.name.ilike(search_term),
                models.DBEmployee.email.ilike(search_term),
                models.DBEmployee.employee_code.ilike(search_term)
            )
        )
    
    if department_id:
        query = query.filter(models.DBEmployee.department_id == department_id)
    if status:
        query = query.filter(models.DBEmployee.status == status)
    if plant_id:
        query = query.filter(models.DBEmployee.plant_id == plant_id)
    
    total = query.count()
    employees = query.offset(skip).limit(min(limit, 500)).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "count": len(employees),
        "employees": employees
    }

@router.get("/employees/{employee_id}", response_model=schemas.Employee)
def read_employee(
    employee_id: str, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(check_permission("view_employees"))
):
    employee = crud.get_employee(db, employee_id=employee_id)
    if not employee:
        raise HTTPException(403, "Access denied")
    org_id = get_user_org(current_user)
    if org_id is not None and employee.organization_id != org_id:
        raise HTTPException(403, "Access denied")
    return employee

@router.put("/employees/{employee_id}", response_model=schemas.Employee)
def update_employee(
    employee_id: str, 
    employee: schemas.EmployeeCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(check_permission("edit_employee"))
):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if not db_employee:
        raise HTTPException(403, "Access denied")
    org_id = get_user_org(current_user)
    if org_id is not None and db_employee.organization_id != org_id:
        raise HTTPException(403, "Access denied")
    return crud.update_employee(db, employee_id, employee, user_id=current_user["id"])

@router.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: str, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(requires_role("Root", "Business Admin"))
):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if not db_employee:
        raise HTTPException(403, "Access denied")
    org_id = get_user_org(current_user)
    if org_id is not None and db_employee.organization_id != org_id:
        raise HTTPException(403, "Access denied")
    return crud.delete_employee(db, employee_id, current_user_id=current_user["id"])

@router.post("/employees/bulk-import")
async def bulk_import_employees(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(requires_role("Root", "Business Admin"))
):
    errors = []
    created = 0
    org_id = get_user_org(current_user)
    
    try:
        contents = await file.read()
        text_stream = io.StringIO(contents.decode('utf-8'))
        reader = csv.DictReader(text_stream)
        
        for row_num, row in enumerate(reader, 1):
            try:
                clean_row = {k: v for k, v in row.items() if v}
                # If org_id is provided (user not in system-wide mode), force CSV rows to that org.
                if org_id is not None:
                    clean_row['organization_id'] = org_id
                employee_data = schemas.EmployeeCreate(**clean_row)
                crud.create_employee(db, employee_data, user_id=current_user["id"])
                created += 1
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
    except Exception as e:
        raise HTTPException(400, f"Failed to process file: {str(e)}")
    
    return {
        "created": created,
        "errors": errors,
        "total": created + len(errors),
        "message": f"Imported {created} employees with {len(errors)} errors"
    }

# Candidates
@router.get("/candidates", response_model=List[schemas.Candidate])
def get_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_candidates(db, skip=skip, limit=limit)

@router.post("/candidates", response_model=schemas.Candidate)
def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.create_candidate(db, candidate, user_id=current_user["id"])

# Job Vacancies
@router.get("/jobs", response_model=List[schemas.JobVacancy])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_job_vacancies(db, skip=skip, limit=limit)

@router.post("/jobs", response_model=schemas.JobVacancy)
def create_job(job: schemas.JobVacancyCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.create_job_vacancy(db, job, user_id=current_user["id"])
