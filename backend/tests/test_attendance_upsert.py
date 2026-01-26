"""
Test cases for attendance upsert (Issue 10 - Phase 2)
Tests update-or-insert logic with conflict resolution strategies
"""

import pytest
from sqlalchemy.orm import Session
from backend import crud, schemas, models as hcm_models


@pytest.fixture
def setup_upsert_data(db: Session):
    """Create test data for upsert tests"""
    # Create Org
    org = crud.create_organization(
        db, 
        schemas.OrganizationCreate(id="ORG_UPSERT", name="Upsert Test Org"), 
        "admin"
    )
    
    # Create Department
    dept = hcm_models.DBDepartment(
        id="DEPT_UPSERT",
        name="Operations",
        organization_id="ORG_UPSERT"
    )
    db.add(dept)
    db.commit()
    
    # Create Shift
    shift = hcm_models.DBShift(
        id="SHIFT_UPSERT",
        name="Standard",
        code="STD",
        start_time="09:00",
        end_time="17:00",
        grace_period=15,
        organization_id="ORG_UPSERT"
    )
    db.add(shift)
    db.commit()
    
    # Create Employees
    for i in range(3):
        crud.create_employee(db, schemas.EmployeeCreate(
            id=f"UPSERT_EMP_{i+1}",
            firstName=f"Employee {i+1}",
            lastName="Upsert",
            email=f"upsert_emp{i+1}@test.com",
            organizationId="ORG_UPSERT",
            shift_id="SHIFT_UPSERT",
            department_id="DEPT_UPSERT"
        ), "admin")
    
    db.commit()
    return org


def test_upsert_insert_new_record(db: Session, setup_upsert_data):
    """Test inserting new record via upsert"""
    request = schemas.AttendanceUpsertRequest(
        organizationId="ORG_UPSERT",
        employeeId="UPSERT_EMP_1",
        date="2026-01-22",
        clockIn="09:00",
        clockOut="17:00"
    )
    
    result = crud.upsert_attendance_record(db, "ORG_UPSERT", request, "admin", "smart")
    
    assert result["action"] == "INSERT"
    assert result["message"]
    
    # Verify record exists
    record = db.query(hcm_models.DBAttendance).filter_by(
        employee_id="UPSERT_EMP_1",
        date="2026-01-22"
    ).first()
    assert record is not None


def test_upsert_smart_identical_skip(db: Session, setup_upsert_data):
    """Test smart strategy skips identical records"""
    # Create initial record
    crud.create_attendance_record(
        db,
        schemas.AttendanceCreate(
            organizationId="ORG_UPSERT",
            employeeId="UPSERT_EMP_1",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"
        ),
        "admin",
        "ORG_UPSERT"
    )
    
    # Upsert same record
    request = schemas.AttendanceUpsertRequest(
        organizationId="ORG_UPSERT",
        employeeId="UPSERT_EMP_1",
        date="2026-01-22",
        clockIn="09:00",
        clockOut="17:00"
    )
    
    result = crud.upsert_attendance_record(db, "ORG_UPSERT", request, "admin", "smart")
    
    assert result["action"] == "SKIP"


def test_upsert_smart_update_different_times(db: Session, setup_upsert_data):
    """Test smart strategy updates different times"""
    # Create initial record
    crud.create_attendance_record(
        db,
        schemas.AttendanceCreate(
            organizationId="ORG_UPSERT",
            employeeId="UPSERT_EMP_1",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"
        ),
        "admin",
        "ORG_UPSERT"
    )
    
    # Upsert with different times
    request = schemas.AttendanceUpsertRequest(
        organizationId="ORG_UPSERT",
        employeeId="UPSERT_EMP_1",
        date="2026-01-22",
        clockIn="09:30",
        clockOut="17:30"
    )
    
    result = crud.upsert_attendance_record(db, "ORG_UPSERT", request, "admin", "smart")
    
    assert result["action"] == "UPDATE"


def test_upsert_overwrite_strategy(db: Session, setup_upsert_data):
    """Test overwrite strategy always updates"""
    # Create initial record
    crud.create_attendance_record(
        db,
        schemas.AttendanceCreate(
            organizationId="ORG_UPSERT",
            employeeId="UPSERT_EMP_1",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"
        ),
        "admin",
        "ORG_UPSERT"
    )
    
    # Upsert with same times
    request = schemas.AttendanceUpsertRequest(
        organizationId="ORG_UPSERT",
        employeeId="UPSERT_EMP_1",
        date="2026-01-22",
        clockIn="09:00",
        clockOut="17:00"
    )
    
    result = crud.upsert_attendance_record(db, "ORG_UPSERT", request, "admin", "overwrite")
    
    assert result["action"] == "UPDATE"


def test_upsert_preserve_strategy(db: Session, setup_upsert_data):
    """Test preserve strategy keeps existing"""
    # Create initial record
    crud.create_attendance_record(
        db,
        schemas.AttendanceCreate(
            organizationId="ORG_UPSERT",
            employeeId="UPSERT_EMP_1",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"
        ),
        "admin",
        "ORG_UPSERT"
    )
    
    # Upsert with different times
    request = schemas.AttendanceUpsertRequest(
        organizationId="ORG_UPSERT",
        employeeId="UPSERT_EMP_1",
        date="2026-01-22",
        clockIn="10:00",
        clockOut="18:00"
    )
    
    result = crud.upsert_attendance_record(db, "ORG_UPSERT", request, "admin", "preserve")
    
    assert result["action"] == "SKIP"


def test_upsert_bulk_mixed_operations(db: Session, setup_upsert_data):
    """Test bulk upsert with mixed insert/update/skip"""
    # Create one existing record
    crud.create_attendance_record(
        db,
        schemas.AttendanceCreate(
            organizationId="ORG_UPSERT",
            employeeId="UPSERT_EMP_1",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"
        ),
        "admin",
        "ORG_UPSERT"
    )
    
    records = [
        schemas.AttendanceUpsertRequest(
            organizationId="ORG_UPSERT",
            employeeId="UPSERT_EMP_1",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"  # Same - will SKIP
        ),
        schemas.AttendanceUpsertRequest(
            organizationId="ORG_UPSERT",
            employeeId="UPSERT_EMP_2",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"  # New - will INSERT
        )
    ]
    
    result = crud.upsert_bulk_attendance_records(
        db,
        "ORG_UPSERT",
        records,
        "admin",
        "smart"
    )
    
    assert result["total"] == 2
    assert result["inserted"] == 1
    assert result["skipped"] == 1
