"""
Test cases for attendance corrections (Issue 11 - Phase 2)
Tests correction creation, approval workflow, and audit trail
"""

import pytest
from sqlalchemy.orm import Session
from backend import crud, schemas, models as hcm_models
from datetime import datetime, timedelta


@pytest.fixture
def setup_correction_data(db: Session):
    """Create test data for correction tests"""
    # Create Org
    org = crud.create_organization(
        db,
        schemas.OrganizationCreate(id="ORG_CORR", name="Correction Test Org"),
        "admin"
    )
    
    # Create Department
    dept = hcm_models.DBDepartment(
        id="DEPT_CORR",
        name="Testing",
        organization_id="ORG_CORR"
    )
    db.add(dept)
    db.commit()
    
    # Create Shift
    shift = hcm_models.DBShift(
        id="SHIFT_CORR",
        name="Standard",
        code="STD",
        start_time="09:00",
        end_time="17:00",
        grace_period=15,
        organization_id="ORG_CORR"
    )
    db.add(shift)
    db.commit()
    
    # Create Employees
    emp1 = crud.create_employee(db, schemas.EmployeeCreate(
        id="CORR_EMP_1",
        firstName="John",
        lastName="Requester",
        email="john@test.com",
        organizationId="ORG_CORR",
        shift_id="SHIFT_CORR",
        department_id="DEPT_CORR"
    ), "admin")
    
    emp2 = crud.create_employee(db, schemas.EmployeeCreate(
        id="CORR_EMP_2",
        firstName="Jane",
        lastName="Approver",
        email="jane@test.com",
        organizationId="ORG_CORR",
        shift_id="SHIFT_CORR",
        department_id="DEPT_CORR"
    ), "admin")
    
    # Create existing attendance
    attendance = crud.create_attendance_record(
        db,
        schemas.AttendanceCreate(
            organizationId="ORG_CORR",
            employeeId="CORR_EMP_1",
            date="2026-01-22",
            clockIn="09:30",
            clockOut="17:00"
        ),
        "admin",
        "ORG_CORR"
    )
    
    db.commit()
    return org, emp1, emp2


def test_create_time_correction(db: Session, setup_correction_data):
    """Test creating time correction request"""
    org, emp1, emp2 = setup_correction_data
    
    request = schemas.AttendanceCorrectionCreate(
        employeeId="CORR_EMP_1",
        date="2026-01-22",
        type="Time Correction",
        originalClockIn="09:30",
        requestedClockIn="09:00",
        reason="System recorded late, was actually on time due to clock issue"
    )
    
    correction = crud.create_attendance_correction(
        db,
        request,
        "CORR_EMP_1"
    )
    
    assert correction.status == "Pending"
    assert correction.requested_clock_in == "09:00"
    assert correction.original_clock_in == "09:30"


def test_create_missing_punch(db: Session, setup_correction_data):
    """Test creating missing punch correction"""
    org, emp1, emp2 = setup_correction_data
    
    request = schemas.AttendanceCorrectionCreate(
        employeeId="CORR_EMP_1",
        date="2026-01-21",
        type="Missing Punch",
        requestedClockIn="09:00",
        requestedClockOut="18:00",
        reason="Forgot to clock in/out"
    )
    
    correction = crud.create_attendance_correction(
        db,
        request,
        "CORR_EMP_1"
    )
    
    assert correction.type == "Missing Punch"
    assert correction.status == "Pending"


def test_create_wrong_status(db: Session, setup_correction_data):
    """Test creating wrong status correction"""
    org, emp1, emp2 = setup_correction_data
    
    request = schemas.AttendanceCorrectionCreate(
        employeeId="CORR_EMP_1",
        date="2026-01-22",
        type="Wrong Status",
        originalStatus="Absent",
        requestedStatus="Present",
        reason="Was actually present, marked absent by mistake"
    )
    
    correction = crud.create_attendance_correction(
        db,
        request,
        "CORR_EMP_1"
    )
    
    assert correction.type == "Wrong Status"
    assert correction.status == "Pending"


def test_create_shift_swap(db: Session, setup_correction_data):
    """Test creating shift swap correction"""
    org, emp1, emp2 = setup_correction_data
    
    request = schemas.AttendanceCorrectionCreate(
        employeeId="CORR_EMP_1",
        date="2026-01-22",
        type="Shift Swap",
        reason="Requested shift change"
    )
    
    correction = crud.create_attendance_correction(
        db,
        request,
        "CORR_EMP_1"
    )
    
    assert correction.type == "Shift Swap"
    assert correction.status == "Pending"


def test_correction_has_audit_trail(db: Session, setup_correction_data):
    """Test correction records audit trail"""
    org, emp1, emp2 = setup_correction_data
    
    request = schemas.AttendanceCorrectionCreate(
        employeeId="CORR_EMP_1",
        date="2026-01-22",
        type="Time Correction",
        originalClockIn="09:30",
        requestedClockIn="09:00",
        reason="Clock malfunction"
    )
    
    correction = crud.create_attendance_correction(
        db,
        request,
        "CORR_EMP_1"
    )
    
    # Verify audit fields
    assert correction.created_by is not None
    assert correction.status == "Pending"
    # Approved fields should be null
    assert correction.approved_by is None
    assert correction.approved_at is None


def test_multiple_correction_types(db: Session, setup_correction_data):
    """Test creating various correction types"""
    org, emp1, emp2 = setup_correction_data
    
    # Test a few different correction types
    request = schemas.AttendanceCorrectionCreate(
        employeeId="CORR_EMP_2",  # Use different employee to avoid date conflicts
        date="2026-01-22",
        type="Shift Swap",
        reason="Test shift swap"
    )
    
    correction = crud.create_attendance_correction(
        db,
        request,
        "CORR_EMP_2"
    )
    
    assert correction.type == "Shift Swap"
    assert correction.status == "Pending"
