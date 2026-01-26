import os
import sys
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import crud, schemas
from backend.database import SessionLocal
from backend.domains.hcm import models as hcm_models
from backend.domains.core import models as core_models

def verify_overtime():
    db = SessionLocal()
    try:
        print("Starting Overtime Verification (Employee Approver)...")
        
        # 1. Get real Org, Employee, and User
        org = db.query(core_models.DBOrganization).first()
        if not org:
            print("FAILURE: No organization found in DB. Run seed first.")
            return
        
        emp = db.query(hcm_models.DBEmployee).filter(hcm_models.DBEmployee.organization_id == org.id).first()
        if not emp:
            print("FAILURE: No employee found in DB. Run seed first.")
            return

        user = db.query(core_models.DBUser).first()
        if not user:
            print("FAILURE: No user found in DB. Run seed first.")
            return

        # For OT Approval, approved_by is FK to hcm_employees.id
        # We'll use the employee themselves as the "approver" for this test
        approver_id = emp.id 

        test_date = "2024-07-23"
        test_hours = 2.5
        
        print(f"Using Org: {org.id}, Employee: {emp.id}, Approver (Employee): {approver_id}, Action User: {user.id}")

        # 2. Setup Attendance Record
        attendance = db.query(hcm_models.DBAttendance).filter(
            hcm_models.DBAttendance.employee_id == emp.id,
            hcm_models.DBAttendance.date == test_date
        ).first()
        if attendance:
            db.delete(attendance)
            db.commit()
            
        attendance = hcm_models.DBAttendance(
            organization_id=org.id,
            employee_id=emp.id,
            date=test_date,
            status="Present",
            overtime_hours=0.0
        )
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        print(f"Initial Attendance OT Hours: {attendance.overtime_hours}")

        # 3. Create Overtime Request
        print("Creating Overtime Request...")
        ot_create = schemas.OvertimeRequestCreate(
            employeeId=emp.id,
            date=test_date,
            hours=test_hours,
            multiplier=1.5,
            reason="Night shift support - Verification"
        )
        
        ot_req = crud.create_overtime_request(db, ot_create, user_id=user.id, org_id=org.id)
        print(f"Created OT Request: {ot_req.id}, Status: {ot_req.status}")

        # 4. Approve Overtime Request
        print("Approving Overtime Request...")
        approved_req = crud.approve_overtime_request(
            db, 
            request_id=ot_req.id, 
            action="approve", 
            approver_id=approver_id
        )
        print(f"Approved OT Request Status: {approved_req.status}")

        # 5. Verify Sync with Attendance
        db.refresh(attendance)
        print(f"Final Attendance OT Hours: {attendance.overtime_hours}")

        if attendance.overtime_hours == test_hours:
            print("SUCCESS: Overtime calculation synced with Attendance correctly.")
        else:
            print(f"FAILURE: Expected {test_hours}, got {attendance.overtime_hours}")

    except Exception as e:
        print(f"An error occurred during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_overtime()
