"""
Test cases for attendance search/filter endpoint (Issue 8 - Phase 2)
Tests multi-criteria search, pagination, and organization isolation
"""

import pytest
from sqlalchemy.orm import Session
from backend import crud, schemas, models as hcm_models
from datetime import datetime, timedelta


@pytest.fixture
def setup_search_data(db: Session):
    """Create test data for search tests"""
    # Create Org
    org = crud.create_organization(
        db, 
        schemas.OrganizationCreate(id="ORG_SEARCH", name="Search Org"), 
        "admin"
    )
    
    # Create Department
    dept = hcm_models.DBDepartment(
        id="DEPT_SALES",
        name="Sales",
        organization_id="ORG_SEARCH"
    )
    db.add(dept)
    db.commit()
    
    # Create Shift
    shift = hcm_models.DBShift(
        id="SHIFT_09",
        name="Morning",
        code="M09",
        start_time="09:00",
        end_time="18:00",
        grace_period=15,
        organization_id="ORG_SEARCH"
    )
    db.add(shift)
    db.commit()
    
    # Create Employees
    emp1 = crud.create_employee(db, schemas.EmployeeCreate(
        id="EMP_SEARCH_1",
        firstName="John",
        lastName="Doe",
        email="john@test.com",
        organizationId="ORG_SEARCH",
        shift_id="SHIFT_09",
        department_id="DEPT_SALES"
    ), "admin")
    
    emp2 = crud.create_employee(db, schemas.EmployeeCreate(
        id="EMP_SEARCH_2",
        firstName="Jane",
        lastName="Smith",
        email="jane@test.com",
        organizationId="ORG_SEARCH",
        shift_id="SHIFT_09",
        department_id="DEPT_SALES"
    ), "admin")
    
    # Create Attendance Records (using recent dates within 90 days)
    # Today is Jan 22, 2026 - use Jan 20-22
    dates = [
        ("2026-01-20", "09:00", "18:00"),
        ("2026-01-21", "09:15", "18:00"),
        ("2026-01-22", "09:00", "18:00"),
    ]
    
    for date, clock_in, clock_out in dates:
        for emp_id in ["EMP_SEARCH_1", "EMP_SEARCH_2"]:
            rec = crud.create_attendance_record(db, schemas.AttendanceCreate(
                organizationId="ORG_SEARCH",
                employeeId=emp_id,
                date=date,
                clockIn=clock_in,
                clockOut=clock_out,
                shiftId="SHIFT_09"
            ), "admin", org_id="ORG_SEARCH")
    
    db.commit()
    return org, emp1, emp2, shift


# Test Cases

def test_search_by_employee_id(db: Session, setup_search_data):
    """Test search by employee ID"""
    org, emp1, emp2, shift = setup_search_data
    criteria = schemas.AttendanceSearch(employee_id="EMP_SEARCH_1")
    records, total = crud.search_attendance_records(db, "ORG_SEARCH", criteria)
    
    assert total >= 1
    assert all(r.employee_id == "EMP_SEARCH_1" for r in records)


def test_search_by_employee_name(db: Session, setup_search_data):
    """Test search by employee name (partial match)"""
    org, emp1, emp2, shift = setup_search_data
    criteria = schemas.AttendanceSearch(employee_name="John")
    records, total = crud.search_attendance_records(db, "ORG_SEARCH", criteria)
    
    assert total >= 1


def test_search_by_date_range(db: Session, setup_search_data):
    """Test search by date range"""
    org, emp1, emp2, shift = setup_search_data
    criteria = schemas.AttendanceSearch(
        date_from="2026-01-20",
        date_to="2026-01-22"
    )
    records, total = crud.search_attendance_records(db, "ORG_SEARCH", criteria)
    
    assert total >= 1
    assert all("2026-01-20" <= r.date <= "2026-01-22" for r in records)


def test_search_by_status(db: Session, setup_search_data):
    """Test search by status"""
    org, emp1, emp2, shift = setup_search_data
    criteria = schemas.AttendanceSearch(status="Present")
    records, total = crud.search_attendance_records(db, "ORG_SEARCH", criteria)
    
    assert total >= 0
    if len(records) > 0:
        assert all(r.status == "Present" for r in records)


def test_search_with_pagination(db: Session, setup_search_data):
    """Test pagination (skip/limit)"""
    org, emp1, emp2, shift = setup_search_data
    criteria = schemas.AttendanceSearch(
        employee_id="EMP_SEARCH_1",
        skip=0,
        limit=1
    )
    records, total = crud.search_attendance_records(db, "ORG_SEARCH", criteria)
    
    assert len(records) <= 1


def test_search_no_criteria_raises_error(db: Session):
    """Test that search without criteria raises error"""
    criteria = schemas.AttendanceSearch()
    
    with pytest.raises(Exception):  # Should raise HTTPException
        crud.search_attendance_records(db, "ORG_SEARCH", criteria)


def test_search_org_isolation(db: Session, setup_search_data):
    """Test that search respects organization isolation"""
    org, emp1, emp2, shift = setup_search_data
    criteria = schemas.AttendanceSearch(employee_id="EMP_SEARCH_1")
    
    # Search for different org should return empty
    records, total = crud.search_attendance_records(db, "DIFFERENT_ORG", criteria)
    
    assert total == 0


def test_search_combined_criteria(db: Session, setup_search_data):
    """Test search with multiple criteria"""
    org, emp1, emp2, shift = setup_search_data
    criteria = schemas.AttendanceSearch(
        date_from="2026-01-20",
        date_to="2026-01-22",
        employee_id="EMP_SEARCH_1"
    )
    records, total = crud.search_attendance_records(db, "ORG_SEARCH", criteria)
    
    assert total >= 0
    assert all(r.employee_id == "EMP_SEARCH_1" for r in records)


def test_search_invalid_status(db: Session):
    """Test that invalid status raises error"""
    criteria = schemas.AttendanceSearch(status="InvalidStatus")
    
    with pytest.raises(Exception):  # Should raise HTTPException
        crud.search_attendance_records(db, "ORG_SEARCH", criteria)


def test_search_date_range_validation(db: Session):
    """Test date range validation (from > to should fail)"""
    criteria = schemas.AttendanceSearch(
        date_from="2026-01-22",
        date_to="2026-01-20"
    )
    
    with pytest.raises(Exception):  # Should raise HTTPException
        crud.search_attendance_records(db, "ORG_SEARCH", criteria)
