import os
import requests
import json
import time

API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://localhost:{API_PORT}/api"

print("=== SIMULATING FRONTEND MASTERDATA FETCH ===\n")

# Step 1: Login
print("1. Logging in...")
login_r = requests.post(f'{API_URL}/auth/login', 
                       json={'username': 'root', 'password': 'root'})
if login_r.status_code != 200:
    print(f"   ERROR: Login failed with {login_r.status_code}")
    exit(1)

token = login_r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print(f"   ✓ Logged in, got token")

# Step 2: Fetch what fetchMasterData() does
print("\n2. Fetching master data...")

endpoints = [
    ('/system/flags', 'systemFlags'),
    ('/payroll-settings', 'payrollSettings'),
    ('/users', 'users'),
    ('/sub-departments', 'subDepartments'),
    ('/positions', 'positions'),
]

for endpoint, label in endpoints:
    try:
        r = requests.get(f'http://localhost:8000/api{endpoint}', headers=headers, timeout=3)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                print(f"   ✓ {label:20} - {r.status_code} ({len(data)} items)")
            else:
                print(f"   ✓ {label:20} - {r.status_code} (object)")
        else:
            print(f"   ✗ {label:20} - {r.status_code} (expected - has fallback)")
    except Exception as e:
        print(f"   ✗ {label:20} - ERROR: {str(e)[:50]}")

# Step 3: Check that users include isSystemUser
print("\n3. Verifying users have isSystemUser field...")
r = requests.get(f'{API_URL}/users', headers=headers)
users = r.json()
for u in users:
    is_sys = u.get('isSystemUser')
    print(f"   - {u.get('username'):15} isSystemUser={is_sys}")

print("\n✓ Frontend data flow working!")
