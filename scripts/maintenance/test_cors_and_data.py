import requests
import json

# Login
print("Testing authentication and CORS...\n")
login_r = requests.post('http://127.0.0.1:8000/api/v1/auth/login', json={'username': 'root', 'password': 'root'})
print(f'1. Login endpoint: {login_r.status_code}')
token = login_r.json()['access_token']

# Test users endpoint
headers = {
    'Authorization': f'Bearer {token}',
    'Origin': 'http://localhost:5173'
}
r = requests.get('http://127.0.0.1:8000/api/v1/users', headers=headers)
print(f'2. Users endpoint: {r.status_code}')
print(f'3. CORS header set: {"access-control-allow-origin" in r.headers}')

if r.status_code == 200:
    users = r.json()
    print(f'\n4. Users returned: {len(users)}')
    for u in users:
        print(f'   - {u.get("username"):15} | role={u.get("role"):12} | isSystemUser={u.get("isSystemUser")}')
else:
    print(f'\nError: {r.text[:300]}')
