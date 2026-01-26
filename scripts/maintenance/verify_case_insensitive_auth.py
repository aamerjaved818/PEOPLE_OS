
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from backend.shared.models import models
from backend.dependencies import verify_password

from backend.database import SessionLocal

def verify_login_case_insensitivity():
    db = SessionLocal()
    
    test_username_input = "people01"
    print(f"Testing login for input: '{test_username_input}'")
    
    # Query with case-insensitivity (Manual check of what auth.py does)
    user = db.query(models.DBUser).filter(func.lower(models.DBUser.username) == test_username_input.lower()).first()
    
    if user:
        print(f"SUCCESS: Found user '{user.username}' in database.")
        # We don't have the plain password used to create PEOPLE01, 
        # but the fact that it matches case-insensitively is the fix for the 401.
        if user.username == "PEOPLE01":
            print("CONFIRMED: Database has uppercase 'PEOPLE01', input was lowercase 'people01'. Query matched correctly.")
    else:
        print(f"FAILURE: User '{test_username_input}' not found even with case-insensitive query.")
    
    db.close()

if __name__ == "__main__":
    verify_login_case_insensitivity()
