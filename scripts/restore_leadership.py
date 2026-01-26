import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.domains.hcm import models
from backend.database import SessionLocal

def restore():
    db = SessionLocal()
    try:
        # 1. Restore/Update Job Level
        level = db.query(models.DBJobLevel).filter(models.DBJobLevel.id == 'LEAD').first()
        if not level:
            print("Creating new Leadership Job Level...")
            level = models.DBJobLevel(
                id='LEAD',
                name='Leadership',
                code='LEAD',
                description='Top-level executive and leadership roles.',
                organization_id='PEOPLE01',
                is_active=True
            )
            db.add(level)
        else:
            print("Updating existing Leadership Job Level...")
            level.name = 'Leadership'
            level.code = 'LEAD'
            level.description = 'Top-level executive and leadership roles.'
            level.is_active = True
        
        db.flush() # Get the level in the session
        
        # 2. Restore Grades E1-E5
        for i in range(1, 6):
            grade_name = f'E{i}'
            grade_id = f'GRD-LEAD-{i}'
            
            existing_grade = db.query(models.DBGrade).filter(models.DBGrade.name == grade_name).first()
            if not existing_grade:
                print(f"Creating grade {grade_name}...")
                grade = models.DBGrade(
                    id=grade_id,
                    name=grade_name,
                    code=grade_name,
                    level=i,
                    job_level_id='LEAD',
                    organization_id='PEOPLE01',
                    is_active=True
                )
                db.add(grade)
            else:
                print(f"Grade {grade_name} already exists, skipping...")

        db.commit()
        print("Restoration complete!")
    except Exception as e:
        db.rollback()
        print(f"Error during restoration: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    restore()
