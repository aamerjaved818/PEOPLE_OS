import requests
import json

# Test 1: Direct connection
print('TEST 1: Direct Python request')
try:
    r = requests.get('http://localhost:8000/api/v1/health', timeout=3)
    print(f'  Status: {r.status_code}')
except Exception as e:
    print(f'  Error: {e}')

# Test 2: With browser origin headers
print('\nTEST 2: With browser Origin header (CORS preflight)')
headers = {'Origin': 'http://localhost:5173'}
try:
    r = requests.options('http://localhost:8000/api/v1/health', headers=headers, timeout=3)
    print(f'  Preflight Status: {r.status_code}')
    allow_origin = r.headers.get('access-control-allow-origin', 'NOT SET')
    print(f'  CORS Allow-Origin: {allow_origin}')
except Exception as e:
    print(f'  Error: {e}')

# Test 3: Login endpoint
print('\nTEST 3: Login endpoint')
try:
    r = requests.post('http://localhost:8000/api/v1/auth/login', 
                     json={'username': 'root', 'password': 'root'}, 
                     timeout=3)
    print(f'  Status: {r.status_code}')
    if r.status_code == 200:
        print(f'  Token received: Yes')
except Exception as e:
    print(f'  Error: {e}')

# Test 4: Users endpoint with auth
print('\nTEST 4: Users endpoint (needs auth)')
try:
    login_r = requests.post('http://localhost:8000/api/v1/auth/login', 
                           json={'username': 'root', 'password': 'root'})
    token = login_r.json()['access_token']
    
    r = requests.get('http://localhost:8000/api/v1/users', 
                    headers={'Authorization': f'Bearer {token}'}, 
                    timeout=3)
    print(f'  Status: {r.status_code}')
    if r.status_code == 200:
        users = r.json()
        print(f'  Users returned: {len(users)}')
except Exception as e:
    print(f'  Error: {e}')
