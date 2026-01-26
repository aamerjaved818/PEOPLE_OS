"""
Monitor backend activity by watching API calls
Shows what data is being requested when you navigate
"""
import os
import requests
import json
import time
from datetime import datetime

# Configuration from environment
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://localhost:{API_PORT}/api"

print("\n" + "="*80)
print(" "*20 + "PEOPLE OS API MONITOR")
print("="*80)
print("\nThis script shows API calls being made to the backend.")
print("Open your browser and navigate to the System Administrators page to see activity.\n")

# Get auth token first
try:
    login_r = requests.post(
        f'{API_URL}/auth/login',
        json={'username': 'root', 'password': 'root'},
        timeout=5
    )
    if login_r.status_code != 200:
        print("ERROR: Could not authenticate. Is the backend running?")
        exit(1)
    
    token = login_r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✓ Authenticated as root user\n")
    
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

# Monitor key endpoints
endpoints = [
    ('users', '/users'),
    ('system/flags', '/system/flags'),
    ('payroll-settings', '/payroll-settings'),
]

print("Monitoring endpoints (refreshing every 2 seconds):\n")

previous_data = {}

while True:
    try:
        for name, endpoint in endpoints:
            r = requests.get(f'{API_URL}{endpoint}', headers=headers, timeout=2)
            
            if r.status_code == 200:
                data = r.json()
                current_hash = str(hash(json.dumps(data, sort_keys=True, default=str)))
                
                # Check if data changed
                if name not in previous_data or previous_data[name] != current_hash:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    if isinstance(data, list):
                        print(f"[{timestamp}] {name:20} → {r.status_code} ({len(data)} items)")
                        if name == 'users':
                            for u in data:
                                sys_flag = '✓ SYSTEM' if u.get('isSystemUser') else '  org user'
                                print(f"              └─ {u.get('username'):15} {sys_flag}")
                    else:
                        print(f"[{timestamp}] {name:20} → {r.status_code} (object)")
                    
                    previous_data[name] = current_hash
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {name:20} → {r.status_code} ERROR")
        
        print("")
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\n[Monitoring stopped]")
        break
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {str(e)[:80]}")
        time.sleep(2)
