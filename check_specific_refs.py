from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.domains.hcm import models

def check_refs():
    db = SessionLocal()
    try:
        grade_id = "GRD-1768459845"
        desig_id = "DSG-1768468565"
        
        grade = db.query(models.DBGrade).filter(models.DBGrade.id == grade_id).first()
        desig = db.query(models.DBDesignation).filter(models.DBDesignation.id == desig_id).first()
        
        print(f"Checking Grade ID: {grade_id}")
        if grade:
            print(f"FOUND Grade: {grade.name}")
            if grade.job_level:
                 print(f"  -> Job Level found: {grade.job_level.name}")
            else:
                 print("  -> Job Level NOT found rel!")
        else:
            print("NOT FOUND Grade")

        print(f"Checking Designation ID: {desig_id}")
        if desig:
            print(f"FOUND Designation: {desig.name}")
        else:
            print("NOT FOUND Designation")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_refs()
