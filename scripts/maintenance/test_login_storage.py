import os
import requests
import json
import time

API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://localhost:{API_PORT}/api"

# Test the complete login and verify what gets stored
time.sleep(2)

resp = requests.post(
    f'{API_URL}/auth/login',
    json={'username': 'root', 'password': 'root'}
)

if resp.status_code == 200:
    data = resp.json()
    user = data['user']
    
    print("=" * 60)
    print("Login Response User Object:")
    print("=" * 60)
    print(json.dumps(user, indent=2))
    
    print("\n" + "=" * 60)
    print("Checking fields that frontend will use:")
    print("=" * 60)
    print(f"username: {user.get('username')}")
    print(f"role: {user.get('role')}")
    print(f"isSystemUser: {user.get('isSystemUser')}")
    print(f"id: {user.get('id')}")
    
    # Check if secureStorage would get the right data
    stored_user = {
        'id': user.get('id'),
        'username': user.get('username'),
        'role': user.get('role'),
        'name': user.get('name'),
        'email': user.get('email'),
        'isSystemUser': user.get('isSystemUser'),
        'organizationId': user.get('organization_id'),
        'employeeId': user.get('employeeId'),
        'status': user.get('status', 'Active'),
    }
    
    print("\n" + "=" * 60)
    print("What frontend would store in secureStorage:")
    print("=" * 60)
    print(json.dumps(stored_user, indent=2))
    
else:
    print(f"Login failed: {resp.status_code}")
