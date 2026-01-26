import requests
import time

time.sleep(2)  # Wait for backend to start

try:
    # Login with root/root
    login_resp = requests.post(
        'http://localhost:8000/api/v1/auth/login',
        json={'username': 'root', 'password': 'root'},
        timeout=5
    )
    
    print(f'Login Status: {login_resp.status_code}')
    if login_resp.ok:
        token_data = login_resp.json()
        token = token_data.get('access_token')
        print(f'✓ Login successful with root/root')
        print(f'Token: {token[:50]}...')
        
        # Now use the token to get users
        headers = {'Authorization': f'Bearer {token}'}
        users_resp = requests.get(
            'http://localhost:8000/api/v1/users',
            headers=headers,
            timeout=5
        )
        
        print(f'\nUsers API Status: {users_resp.status_code}')
        if users_resp.ok:
            users = users_resp.json()
            print(f'\n=== All Users ===')
            for u in users:
                is_sys = u.get('isSystemUser', u.get('is_system_user'))
                role = u.get('role')
                print(f'  {u.get("username"):15} | Role: {role:12} | isSystemUser: {is_sys}')
            
            # Filter system users (for the frontend)
            system_users = [u for u in users if u.get('isSystemUser', u.get('is_system_user')) == True]
            print(f'\n=== System Administrators (isSystemUser=True) ===')
            for u in system_users:
                print(f'  {u.get("username"):15} | Role: {u.get("role")}')
        else:
            print(f'Error getting users: {users_resp.text[:200]}')
    else:
        print(f'Login failed: {login_resp.status_code}')
        print(f'Response: {login_resp.text[:200]}')
        
except Exception as e:
    print(f'Exception: {e}')
