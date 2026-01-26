import os
import requests
import time

API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://localhost:{API_PORT}/api"

time.sleep(2)  # Wait for backend to start

try:
    # Try to login with the Root user we created
    login_resp = requests.post(
        f'{API_URL}/auth/login',
        json={'username': '.amer', 'password': 'RootAdmin123!'},
        timeout=5
    )
    
    print(f'Login Status: {login_resp.status_code}')
    if login_resp.ok:
        token_data = login_resp.json()
        token = token_data.get('access_token')
        print(f'Token obtained: {token[:50] if token else "None"}...')
        
        # Now use the token to get users
        headers = {'Authorization': f'Bearer {token}'}
        users_resp = requests.get(
            f'{API_URL}/users',
            headers=headers,
            timeout=5
        )
        
        print(f'\nUsers Status: {users_resp.status_code}')
        if users_resp.ok:
            users = users_resp.json()
            print(f'Found {len(users)} users:\n')
            for u in users:
                is_sys = u.get('isSystemUser', u.get('is_system_user'))
                print(f'  {u.get("username"):15} | {u.get("role"):12} | isSystemUser={is_sys}')
        else:
            print(f'Error getting users: {users_resp.text[:200]}')
    else:
        print(f'Login failed: {login_resp.text[:200]}')
        
except Exception as e:
    print(f'Exception: {e}')
