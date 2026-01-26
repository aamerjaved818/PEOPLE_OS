import os
import requests
import json

API_PORT = os.getenv("API_PORT", "8000")

def verify_employee():
    url = f"http://localhost:{API_PORT}/api/employees/ENERGY01-0001"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        print("--- Employee Logic Verification ---")
        print(f"ID: {data.get('id')}")
        print(f"Name: {data.get('name')}")
        
        # Check denormalized fields
        fields_to_check = ['grade', 'employmentLevel', 'designation', 'hrPlant', 'shift', 'department']
        
        all_passed = True
        for field in fields_to_check:
            value = data.get(field)
            if value:
                print(f"[PASS] {field}: {value}")
            else:
                print(f"[FAIL] {field} is missing or empty! Value: {value}")
                all_passed = False
                
        # Also check ID fields for reference
        print(f"Grade ID: {data.get('grade_id')}")
        print(f"Designation ID: {data.get('designation_id')}")
        
        if all_passed:
            print("\nSUCCESS: All fields are populated correctly.")
        else:
            print("\nFAILURE: Some fields are missing.")
            
    except Exception as e:
        print(f"Error: {e}")
        if 'response' in locals():
            print(response.text)

if __name__ == "__main__":
    verify_employee()
