import os
import requests
import json

API_PORT = os.getenv("API_PORT", "8000")
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "5173")
API_URL = f"http://127.0.0.1:{API_PORT}/api"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"

# Login
print("Testing authentication and CORS...\n")
login_r = requests.post(f'{API_URL}/auth/login', json={'username': 'root', 'password': 'root'})
print(f'1. Login endpoint: {login_r.status_code}')
token = login_r.json()['access_token']

# Test users endpoint
headers = {
    'Authorization': f'Bearer {token}',
    'Origin': FRONTEND_URL
}
r = requests.get(f'{API_URL}/users', headers=headers)
print(f'2. Users endpoint: {r.status_code}')
print(f'3. CORS header set: {"access-control-allow-origin" in r.headers}')

if r.status_code == 200:
    users = r.json()
    print(f'\n4. Users returned: {len(users)}')
    for u in users:
        print(f'   - {u.get("username"):15} | role={u.get("role"):12} | isSystemUser={u.get("isSystemUser")}')
else:
    print(f'\nError: {r.text[:300]}')
