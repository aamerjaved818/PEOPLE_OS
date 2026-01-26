import requests
import json

# URL for the employees list endpoint
url = "http://localhost:8001/api/employees?skip=0&limit=10"

try:
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    
    print(f"Status Code: {response.status_code}")
    print(f"Count: {len(data)}")
    
    if len(data) > 0:
        first_emp = data[0]
        print("\nFirst Employee Data Check:")
        print(f"ID: {first_emp.get('id')}")
        print(f"Name: {first_emp.get('name')}")
        print(f"Grade (Property): {first_emp.get('grade')}")
        print(f"Job Level (Property): {first_emp.get('employmentLevel')}")
        
        # Save full dump for inspection
        with open("list_response.json", "w") as f:
            json.dump(data, f, indent=2)
            print("\nFull response saved to list_response.json")
    else:
        print("No employees found.")

except Exception as e:
    print(f"Error: {e}")
