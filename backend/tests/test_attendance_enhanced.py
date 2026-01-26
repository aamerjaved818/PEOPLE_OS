import pytest
from sqlalchemy.orm import Session
from backend import crud, schemas, models as hcm_models
from datetime import datetime, timedelta

@pytest.fixture
def setup_attendance_data(db: Session):
    # Create Org
    org = crud.create_organization(db, schemas.OrganizationCreate(id="ORG_ATT", name="Attendance Org"), "admin")
    
    # Create Shift (09:00 - 18:00, 15m grace)
    shift = hcm_models.DBShift(
        id="SHIFT_09",
        name="Morning Shift",
        code="M09",
        start_time="09:00",
        end_time="18:00",
        grace_period=15,
        organization_id="ORG_ATT"
    )
    db.add(shift)
    
    # Create Employee
    emp = crud.create_employee(db, schemas.EmployeeCreate(
        id="EMP_ATT_1",
        firstName="Alice",
        lastName="Attendance",
        email="alice@test.com",
        organizationId="ORG_ATT",
        shift_id="SHIFT_09"
    ), "admin")
    db.commit()
    return emp, shift

def test_late_detection(db: Session, setup_attendance_data):
    emp, shift = setup_attendance_data
    
    # Clock in at 09:20 (20 mins late, grace is 15)
    rec_data = schemas.AttendanceCreate(
        organizationId="ORG_ATT",
        employeeId=emp.id,
        date="2026-01-22",
        clockIn="09:20",
        shiftId=shift.id
    )
    record = crud.create_attendance_record(db, rec_data, "admin")
    
    assert record.status == "Late"
    assert record.late_minutes == 20

def test_present_detection(db: Session, setup_attendance_data):
    emp, shift = setup_attendance_data
    
    # Clock in at 09:10 (10 mins late, within 15m grace)
    rec_data = schemas.AttendanceCreate(
        organizationId="ORG_ATT",
        employeeId=emp.id,
        date="2026-01-23",
        clockIn="09:10",
        shiftId=shift.id
    )
    record = crud.create_attendance_record(db, rec_data, "admin")
    
    assert record.status == "Present"
    assert record.late_minutes == 10

def test_leave_integration(db: Session, setup_attendance_data):
    emp, shift = setup_attendance_data
    
    # Create Approved Leave
    leave = hcm_models.DBLeaveRequest(
        id="LEAVE_1",
        organization_id="ORG_ATT",
        employee_id=emp.id,
        start_date="2026-01-23",
        end_date="2026-01-23",
        status="Approved",
        type="Casual"
    )
    db.add(leave)
    db.commit()
    
    # Create Attendance for that day
    rec_data = schemas.AttendanceCreate(
        organizationId="ORG_ATT",
        employeeId=emp.id,
        date="2026-01-23"
    )
    record = crud.create_attendance_record(db, rec_data, "admin")
    
    assert record.status == "Leave"

def test_overtime_calculation(db: Session, setup_attendance_data):
    emp, shift = setup_attendance_data
    
    # Clock in 09:00, Clock out 20:00 (2 hours OT)
    rec_data = schemas.AttendanceCreate(
        organizationId="ORG_ATT",
        employeeId=emp.id,
        date="2026-01-20",
        clockIn="09:00",
        clockOut="20:00",
        shiftId=shift.id
    )
    record = crud.create_attendance_record(db, rec_data, "admin")
    
    assert record.overtime_hours == 2.0
    assert record.early_leave == False

def test_early_leave_detection(db: Session, setup_attendance_data):
    emp, shift = setup_attendance_data
    
    # Clock in 09:00, Clock out 16:00 (2 hours early)
    rec_data = schemas.AttendanceCreate(
        organizationId="ORG_ATT",
        employeeId=emp.id,
        date="2026-01-21",
        clockIn="09:00",
        clockOut="16:00",
        shiftId=shift.id
    )
    record = crud.create_attendance_record(db, rec_data, "admin")
    
    assert record.early_leave == True
    assert record.overtime_hours == 0.0

def test_half_day_detection(db: Session, setup_attendance_data):
    emp, shift = setup_attendance_data
    
    # Worked only 2 hours
    rec_data = schemas.AttendanceCreate(
        organizationId="ORG_ATT",
        employeeId=emp.id,
        date="2026-01-22",
        clockIn="09:00",
        clockOut="11:00",
        shiftId=shift.id
    )
    record = crud.create_attendance_record(db, rec_data, "admin")
    
    assert record.status == "Half Day"
