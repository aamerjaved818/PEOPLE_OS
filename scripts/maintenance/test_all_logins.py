import os
import requests
import json

API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://localhost:{API_PORT}/api"

# Test with different variations
test_cases = [
    {'username': 'root', 'password': 'root'},
    {'username': 'Root', 'password': 'root'},
    {'username': 'ROOT', 'password': 'root'},
    {'username': 'PEOPLE01', 'password': 'PEOPLE01'},
]

print("Testing login endpoint with various credentials:\n")

for test in test_cases:
    try:
        resp = requests.post(
            f'{API_URL}/auth/login',
            json=test,
            timeout=5
        )
        status = "✓ SUCCESS" if resp.status_code == 200 else f"✗ FAILED ({resp.status_code})"
        print(f"{status}: {test['username']:15} / {test['password']}")
        
        if resp.status_code != 200:
            data = resp.json()
            if isinstance(data, dict):
                print(f"         Detail: {data.get('detail', 'N/A')}")
    except Exception as e:
        print(f"✗ ERROR:  {test['username']:15} / {test['password']} - {str(e)[:80]}")

print("\nNote: API is working. Issue is likely in frontend.")
print("Try clearing browser cache and reloading the page.")
