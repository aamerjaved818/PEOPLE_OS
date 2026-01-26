import os
import requests
import time
import sys

API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://localhost:{API_PORT}/api"

time.sleep(2)  # Wait for backend to start

try:
    resp = requests.get(f'{API_URL}/users', timeout=5)
    print(f'Status: {resp.status_code}')
    
    if resp.ok:
        users = resp.json()
        print(f'\nFound {len(users)} users:\n')
        for u in users:
            is_sys = u.get('isSystemUser', u.get('is_system_user'))
            print(f'  {u.get("username"):15} | {u.get("role"):12} | isSystemUser={is_sys}')
    else:
        print(f'Error: {resp.status_code} - {resp.text[:200]}')
except Exception as e:
    print(f'Exception: {e}')
    sys.exit(1)
