import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from backend.database import SessionLocal
from backend import schemas, crud

def test_create_root_user():
    db = SessionLocal()
    try:
        user = schemas.UserCreate(
            username="attempt_root",
            password="weakpass",
            role="Root",
            email="attempt@local",
            name="Attempt Root",
        )
        try:
            crud.create_user(db, user, creator_id="script")
            print("ERROR: Root creation was allowed (unexpected)")
        except Exception as e:
            print("Root creation blocked as expected:", str(e))
    finally:
        db.close()

if __name__ == '__main__':
    test_create_root_user()
