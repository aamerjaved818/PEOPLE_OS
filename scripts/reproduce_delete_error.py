import sys
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.domains.core import models as core_models
from backend.domains.hcm import models as hcm_models
from backend import crud

class ModelsProxy:
    def __getattr__(self, name):
        if hasattr(core_models, name):
            return getattr(core_models, name)
        if hasattr(hcm_models, name):
            return getattr(hcm_models, name)
        raise AttributeError(f"Model {name} not found")

models = ModelsProxy()

DATABASE_URL = "sqlite:///backend/data/people_os_dev.db"
engine = create_engine(DATABASE_URL)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_delete_job_level():
    db = SessionLocal()
    try:
        # 1. List some job levels
        levels = db.query(models.DBJobLevel).all()
        if not levels:
            print("No job levels found to delete.")
            return

        level_to_delete = levels[0]
        print(f"Attempting to delete Job Level: ID={level_to_delete.id}, Name={level_to_delete.name}")

        # 2. Check for dependencies
        related_grades = db.query(models.DBGrade).filter(models.DBGrade.job_level_id == level_to_delete.id).all()
        if related_grades:
            print(f"WARNING: Found {len(related_grades)} related grades. This might cause a constraint failure.")
            for g in related_grades:
                print(f"  - Grade: {g.name}")

        # 3. Try to delete
        try:
            success = crud.delete_job_level(db, level_to_delete.id)
            print(f"Deletion result: {success}")
        except Exception as e:
            print(f"ERROR during deletion: {e}")
            db.rollback()

    finally:
        db.close()

if __name__ == "__main__":
    test_delete_job_level()
