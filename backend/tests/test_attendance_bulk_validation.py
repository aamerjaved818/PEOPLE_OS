"""
Test cases for bulk attendance validation (Issue 9 - Phase 2)
Tests line-by-line validation, error reporting, dry-run mode
"""

import pytest
from sqlalchemy.orm import Session
from backend import crud, schemas, models as hcm_models


@pytest.fixture
def setup_bulk_validation_data(db: Session):
    """Create test data for bulk validation tests"""
    # Create Org
    org = crud.create_organization(
        db, 
        schemas.OrganizationCreate(id="ORG_BULK", name="Bulk Test Org"), 
        "admin"
    )
    
    # Create Department
    dept = hcm_models.DBDepartment(
        id="DEPT_ENG",
        name="Engineering",
        organization_id="ORG_BULK"
    )
    db.add(dept)
    
    # Create Shift
    shift = hcm_models.DBShift(
        id="SHIFT_BULK",
        name="Standard",
        code="STD",
        start_time="09:00",
        end_time="17:00",
        grace_period=15,
        organization_id="ORG_BULK"
    )
    db.add(shift)
    
    # Create Plant
    plant = hcm_models.DBHRPlant(
        id="PLANT_BULK",
        name="Main Plant",
        code="MAIN",
        organization_id="ORG_BULK"
    )
    db.add(plant)
    db.commit()
    
    # Create Employees
    for i in range(5):
        emp = crud.create_employee(db, schemas.EmployeeCreate(
            id=f"BULK_EMP_{i+1}",
            firstName=f"Employee {i+1}",
            lastName="Test",
            email=f"bulk_emp{i+1}@test.com",
            organizationId="ORG_BULK",
            shift_id="SHIFT_BULK",
            department_id="DEPT_ENG",
            plant_id="PLANT_BULK",
            status="Active"
        ), "admin")
    
    db.commit()
    return org


def test_bulk_validation_all_valid(db: Session, setup_bulk_validation_data):
    """Test validation of all valid records"""
    records = [
        schemas.AttendanceRecordImport(
            organizationId="ORG_BULK",
            employeeId=f"BULK_EMP_{i+1}",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00",
            status="Present",
            shiftId="SHIFT_BULK"
        )
        for i in range(3)
    ]
    
    result = crud.validate_bulk_attendance_records(db, "ORG_BULK", records, dry_run=True)
    
    assert result["total"] == 3
    assert result["valid"] == 3
    assert result["invalid"] == 0
    assert all(r.valid and r.action == "INSERT" for r in result["results"])


def test_bulk_validation_with_errors(db: Session, setup_bulk_validation_data):
    """Test validation with invalid records"""
    records = [
        schemas.AttendanceRecordImport(
            organizationId="ORG_BULK",
            employeeId="NONEXISTENT",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"
        ),
        schemas.AttendanceRecordImport(
            organizationId="ORG_BULK",
            employeeId="BULK_EMP_1",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00",
            status="InvalidStatus"
        )
    ]
    
    result = crud.validate_bulk_attendance_records(db, "ORG_BULK", records, dry_run=True)
    
    assert result["total"] == 2
    assert result["invalid"] == 2
    assert all(not r.valid and r.action == "ERROR" for r in result["results"])
    assert len(result["error_manifest"]) > 0


def test_bulk_validation_batch_duplicates(db: Session, setup_bulk_validation_data):
    """Test detection of duplicates within batch"""
    records = [
        schemas.AttendanceRecordImport(
            organizationId="ORG_BULK",
            employeeId="BULK_EMP_1",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"
        ),
        schemas.AttendanceRecordImport(
            organizationId="ORG_BULK",
            employeeId="BULK_EMP_1",
            date="2026-01-22",
            clockIn="08:00",
            clockOut="17:00"
        )
    ]
    
    result = crud.validate_bulk_attendance_records(db, "ORG_BULK", records, dry_run=True)
    
    assert result["total"] == 2
    assert result["invalid"] >= 1


def test_bulk_validation_org_isolation(db: Session, setup_bulk_validation_data):
    """Test organization isolation in bulk validation"""
    records = [
        schemas.AttendanceRecordImport(
            organizationId="DIFFERENT_ORG",
            employeeId="BULK_EMP_1",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"
        )
    ]
    
    result = crud.validate_bulk_attendance_records(db, "ORG_BULK", records, dry_run=True)
    
    assert result["invalid"] == 1
    assert "mismatch" in result["results"][0].errors[0].lower()


def test_bulk_validation_dry_run_no_persist(db: Session, setup_bulk_validation_data):
    """Test dry-run mode doesn't persist"""
    initial_count = db.query(hcm_models.DBAttendance).filter(
        hcm_models.DBAttendance.organization_id == "ORG_BULK"
    ).count()
    
    records = [
        schemas.AttendanceRecordImport(
            organizationId="ORG_BULK",
            employeeId=f"BULK_EMP_{i+1}",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"
        )
        for i in range(2)
    ]
    
    crud.validate_bulk_attendance_records(db, "ORG_BULK", records, dry_run=True)
    
    final_count = db.query(hcm_models.DBAttendance).filter(
        hcm_models.DBAttendance.organization_id == "ORG_BULK"
    ).count()
    
    assert final_count == initial_count  # No records added


def test_bulk_validation_persist_on_success(db: Session, setup_bulk_validation_data):
    """Test persistence on successful validation without dry-run"""
    initial_count = db.query(hcm_models.DBAttendance).filter(
        hcm_models.DBAttendance.organization_id == "ORG_BULK"
    ).count()
    
    records = [
        schemas.AttendanceRecordImport(
            organizationId="ORG_BULK",
            employeeId="BULK_EMP_1",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00",
            shiftId="SHIFT_BULK"
        )
    ]
    
    crud.validate_bulk_attendance_records(db, "ORG_BULK", records, dry_run=False)
    
    final_count = db.query(hcm_models.DBAttendance).filter(
        hcm_models.DBAttendance.organization_id == "ORG_BULK"
    ).count()
    
    assert final_count == initial_count + 1  # One record added


def test_bulk_validation_error_manifest(db: Session, setup_bulk_validation_data):
    """Test error manifest CSV generation"""
    records = [
        schemas.AttendanceRecordImport(
            organizationId="ORG_BULK",
            employeeId="INVALID",
            date="2026-01-22",
            clockIn="09:00",
            clockOut="17:00"
        )
    ]
    
    result = crud.validate_bulk_attendance_records(db, "ORG_BULK", records, dry_run=True)
    
    assert "line_number" in result["error_manifest"]
    assert "employee_id" in result["error_manifest"]
    assert "INVALID" in result["error_manifest"]
