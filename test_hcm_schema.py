import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend import schemas
from pydantic import ValidationError

def test_schema():
    print("Testing EmployeeCreate schema flexibility...")
    # Test 1: Missing email and organizationId (should pass now)
    payload = {
        "name": "Test User",
        "firstName": "Test",
        "lastName": "User",
        "employeeCode": "TEST-001"
    }
    try:
        emp = schemas.EmployeeCreate(**payload)
        print("Test 1 Passed: Partial payload validated successfully.")
        print(f"Validated employee_code: {emp.employee_code}")
    except ValidationError as e:
        print(f"Test 1 Failed: {e}")
        return False

    # Test 2: Full payload with aliases
    payload_full = {
        "name": "Full User",
        "firstName": "Full",
        "lastName": "User",
        "employeeCode": "FULL-001",
        "email": "test@example.com",
        "organizationId": "PEOPLE01",
        "plant_id": "LOC01"
    }
    try:
        emp_full = schemas.EmployeeCreate(**payload_full)
        print("Test 2 Passed: Full payload validated successfully.")
    except ValidationError as e:
        print(f"Test 2 Failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if test_schema():
        print("\nAll schema tests passed!")
    else:
        sys.exit(1)
