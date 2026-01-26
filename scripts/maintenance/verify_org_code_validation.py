
from pydantic import ValidationError
from backend.schemas import OrganizationBase

def test_org_code_validation():
    test_cases = [
        ("PEOPLE01", True),   # 6 letters, 2 digits - VALID
        ("ABC01", True),      # 3 letters, 2 digits - VALID (Min)
        ("ABCDEFG01", True),   # 7 letters, 2 digits - VALID (Max)
        ("PEOPLE001", False), # 6 letters, 3 digits - INVALID
        ("PE01", False),      # 2 letters, 2 digits - INVALID (Too short)
        ("ABCDEFGH01", False),# 8 letters, 2 digits - INVALID (Too long)
        ("people01", False),  # Lowercase letters - INVALID
        ("ABCDE", False),     # Letters only - INVALID
        ("12ABC", False),     # Digits first - INVALID (based on regex ^[A-Z]{3,7}[0-9]{2}$)
    ]

    print("--- Testing Organization Code Validation ---")
    success_count = 0
    for code, expected_valid in test_cases:
        try:
            OrganizationBase(code=code)
            is_valid = True
        except ValidationError:
            is_valid = False
        
        if is_valid == expected_valid:
            print(f"PASS: code='{code}', valid={is_valid}")
            success_count += 1
        else:
            print(f"FAIL: code='{code}', expected={expected_valid}, got={is_valid}")

    print(f"\nResults: {success_count}/{len(test_cases)} tests passed.")

if __name__ == "__main__":
    test_org_code_validation()
