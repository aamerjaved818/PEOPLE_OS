import requests
import time

# Test the users API with authentication
time.sleep(2)

# Login first
login_resp = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    json={'username': 'root', 'password': 'root'},
    timeout=5
)

if login_resp.status_code == 200:
    token = login_resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Fetch users multiple times to see if the API returns consistent data
    print("Testing users API multiple times:\n")
    for i in range(3):
        resp = requests.get('http://localhost:8000/api/v1/users', headers=headers, timeout=5)
        if resp.ok:
            users = resp.json()
            print(f"Call {i+1}: Found {len(users)} users")
            for u in users:
                is_sys = u.get('isSystemUser', u.get('is_system_user'))
                print(f"  - {u.get('username'):15} | {u.get('role'):12} | isSystemUser={is_sys}")
            print()
        else:
            print(f"Call {i+1}: Failed with status {resp.status_code}")
        time.sleep(0.5)
else:
    print(f"Login failed: {login_resp.status_code}")
