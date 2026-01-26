from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend import crud, schemas
from backend.database import get_db
from backend.dependencies import (
    check_permission,
    get_user_org
)

router = APIRouter(tags=["HCM - Learning"])

@router.get("/learning/courses", response_model=List[schemas.Course])
def get_courses(
    employee_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("view_employees"))
):
    org_id = get_user_org(current_user)
    return crud.get_courses(db, organization_id=org_id, employee_id=employee_id)

@router.post("/learning/courses", response_model=schemas.Course)
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    org_id = get_user_org(current_user)
    if org_id is not None and not course.organization_id:
        course.organization_id = org_id
    return crud.create_course(db, course, organization_id=org_id, user_id=current_user["id"])

@router.put("/learning/courses/{course_id}/progress", response_model=schemas.Course)
def update_course_progress(
    course_id: int,
    progress: int,
    status: str,
    score: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_permission("edit_employee"))
):
    updated = crud.update_course_progress(db, course_id, progress, status, score)
    if not updated:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated
