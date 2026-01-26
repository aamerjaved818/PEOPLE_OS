import requests
import json

# Test login endpoint to see if isSystemUser is now included
test_users = [
    {'username': 'root', 'password': 'root'},
    {' username': '.amer', 'password': 'amer'},
]

print("Testing login endpoint responses:\n")

for test in test_users:
    try:
        resp = requests.post(
            'http://localhost:8000/api/v1/auth/login',
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
