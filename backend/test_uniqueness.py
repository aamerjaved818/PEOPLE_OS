import sys
import os
# Add current directory to path
sys.path.append(os.getcwd())
# Add parent directory to path since we are in /backend
sys.path.append(os.path.dirname(os.getcwd()))

from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import crud

def main():
	db = SessionLocal()
	plant_id = "LHR01"

	print(f"Initial get for {plant_id}...")
	code1 = crud.get_next_employee_code(db, plant_id)
	print(f"First code: {code1}") # Expected LHR01-001

	print(f"Second get for {plant_id} (collision with 002 expected)...")
	code2 = crud.get_next_employee_code(db, plant_id)
	print(f"Second code: {code2}") # Expected LHR01-003

	db.close()


if __name__ == "__main__":
	main()
