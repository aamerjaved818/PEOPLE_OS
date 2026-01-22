
import sys
import os
from pydantic import ValidationError

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from schemas import EmployeeBase
except ImportError:
    # Try relative import if running from root
    try:
        from backend.schemas import EmployeeBase
    except ImportError:
        print("Could not import EmployeeBase. Check python path.")
        sys.exit(1)

def test_validations():
    print("--- Testing Employee Validations ---")
    
    # 1. Test Invalid CNIC
    print("\n1. Testing Invalid CNIC '123'...")
    try:
        EmployeeBase(cnic="123", name="Test", email="test@example.com", status="Active", join_date="2023-01-01")
        print("❌ FAILED: Invalid CNIC was accepted")
    except ValidationError as e:
        print(f"✅ PASSED: Caught invalid CNIC: {e.errors()[0]['msg']}")

    # 2. Test Valid CNIC (Hyphenated)
    print("\n2. Testing Valid CNIC '12345-1234567-1'...")
    try:
        EmployeeBase(cnic="12345-1234567-1", name="Test", email="test@example.com", status="Active", join_date="2023-01-01")
        print("✅ PASSED: Valid CNIC accepted")
    except ValidationError as e:
        print(f"❌ FAILED: Valid CNIC rejected: {e}")

    # 3. Test Invalid Phone
    print("\n3. Testing Invalid Phone '123'...")
    try:
        EmployeeBase(phone="123", name="Test", email="test@example.com", status="Active", join_date="2023-01-01")
        print("❌ FAILED: Invalid Phone was accepted")
    except ValidationError as e:
        print(f"✅ PASSED: Caught invalid Phone: {e.errors()[0]['msg']}")

    # 4. Test Negative Salary
    print("\n4. Testing Negative Salary -500...")
    try:
        EmployeeBase(gross_salary=-500, name="Test", email="test@example.com", status="Active", join_date="2023-01-01")
        print("❌ FAILED: Negative Salary was accepted")
    except ValidationError as e:
        print(f"✅ PASSED: Caught negative salary: {e.errors()[0]['msg']}")

    print("\n--- Tests Completed ---")

if __name__ == "__main__":
    test_validations()
