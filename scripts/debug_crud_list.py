import sys
import os

# Add local directory to path so we can import backend modules
sys.path.append(os.getcwd())

from backend import crud, schemas
from backend.database import SessionLocal
from backend.domains.hcm import models as hcm_models

def test_list_employees():
    db = SessionLocal()
    try:
        print("Fetching employees...")
        employees = crud.get_employees(db, limit=5)
        print(f"Found {len(employees)} employees")
        
        for emp in employees:
            print(f"\nID: {emp.id}")
            print(f"Name: {emp.name}")
            print(f"Designation: {emp.designation_rel.name if emp.designation_rel else 'None'}")
            print(f"Grade (Rel): {emp.grade_rel.name if emp.grade_rel else 'None'}")
            
            # Check recursive join
            if emp.grade_rel:
                print(f"  > Grade found. Checking JobLevel...")
                # Try accessing job_level - if lazy loading fails or is missing, this might print None or fail
                try:
                    jl = emp.grade_rel.job_level
                    print(f"  > Job Level (Rel): {jl.name if jl else 'None'}")
                except Exception as e:
                    print(f"  > Job Level Access Error: {e}")
            
            # Check Computed Properties
            print(f"Grade (Property): {emp.grade}")
            print(f"EmploymentLevel (Property): {emp.employmentLevel}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_list_employees()
