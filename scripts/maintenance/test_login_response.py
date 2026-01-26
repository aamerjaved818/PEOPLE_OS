import os
import requests
import json

API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://localhost:{API_PORT}/api"

# Test login endpoint to see if isSystemUser is now included
test_users = [
    {'username': 'root', 'password': 'root'},
    {' username': '.amer', 'password': 'amer'},
]

print("Testing login endpoint responses:\n")

for test in test_users:
    try:
        resp = requests.post(
            f'{API_URL}/auth/login',
            json=test,
            timeout=5
        )
        
        if resp.status_code == 200:
            data = resp.json()
            user = data.get('user', {})
            print(f"✓ {test['username']}")
            print(f"  User data: {json.dumps(user, indent=2)}")
            print()
        else:
            print(f"✗ {test['username']}: Status {resp.status_code}")
            print()
    except Exception as e:
        print(f"✗ Error: {e}\n")
