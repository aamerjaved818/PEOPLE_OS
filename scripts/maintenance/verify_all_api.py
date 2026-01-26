"""
Comprehensive API Endpoint Verification
Tests all critical endpoints used by the frontend
"""
import requests
import json
import time
from datetime import datetime

print("\n" + "="*90)
print(" "*25 + "PEOPLE OS API ENDPOINT VERIFICATION")
print("="*90 + "\n")

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def test_endpoint(name, method, endpoint, headers=None, json_data=None, expected_status=200):
    """Test a single endpoint"""
    try:
        url = f'http://localhost:8000/api/v1{endpoint}'
        
        if method == 'GET':
            r = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            r = requests.post(url, headers=headers, json=json_data, timeout=5)
        else:
            return f"UNKNOWN METHOD: {method}"
        
        status_ok = r.status_code == expected_status
        status_color = GREEN if status_ok else RED
        
        response_info = ""
        if r.status_code == 200:
            try:
                data = r.json()
                if isinstance(data, list):
                    response_info = f"({len(data)} items)"
                elif isinstance(data, dict):
                    response_info = f"(object with {len(data)} fields)"
            except:
                pass
        
        status_text = f"{status_color}{r.status_code}{RESET}"
        result = f"{status_text} {response_info}".strip()
        
        return result, status_ok
    
    except requests.Timeout:
        return f"{RED}TIMEOUT{RESET}", False
    except requests.ConnectionError:
        return f"{RED}CONNECTION ERROR{RESET}", False
    except Exception as e:
        return f"{RED}ERROR: {str(e)[:50]}{RESET}", False

# First: Test health
print(f"{BOLD}1. SYSTEM HEALTH{RESET}")
print("-" * 90)
result, ok = test_endpoint("Health", "GET", "/health")
print(f"  GET /health{' ' * 60}{result}")

# Step 2: Login
print(f"\n{BOLD}2. AUTHENTICATION{RESET}")
print("-" * 90)

login_resp = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    json={'username': 'root', 'password': 'root'},
    timeout=5
)

if login_resp.status_code == 200:
    print(f"  POST /auth/login{' ' * 61}{GREEN}200{RESET} (authenticated as root)")
    token = login_resp.json()['access_token']
    user_data = login_resp.json().get('user', {})
    headers = {'Authorization': f'Bearer {token}'}
    auth_ok = True
else:
    print(f"  POST /auth/login{' ' * 61}{RED}FAILED{RESET}")
    auth_ok = False
    exit(1)

# Step 3: Core Data Endpoints (used in fetchMasterData)
print(f"\n{BOLD}3. CORE DATA ENDPOINTS (fetchMasterData){RESET}")
print("-" * 90)

core_endpoints = [
    ("System Flags", "GET", "/system/flags", 200),
    ("Payroll Settings", "GET", "/payroll-settings", 200),
    ("Users", "GET", "/users", 200),
]

core_results = []
for name, method, endpoint, expected in core_endpoints:
    result, ok = test_endpoint(name, method, endpoint, headers=headers, expected_status=expected)
    core_results.append(ok)
    status = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
    print(f"  {status} {name:30} {method:6} {endpoint:35} {result}")

# Step 4: User Management Endpoints
print(f"\n{BOLD}4. USER MANAGEMENT ENDPOINTS{RESET}")
print("-" * 90)

user_endpoints = [
    ("Get All Users", "GET", "/users", 200),
    ("Get Organizations", "GET", "/organizations", 200),
]

user_results = []
for name, method, endpoint, expected in user_endpoints:
    result, ok = test_endpoint(name, method, endpoint, headers=headers, expected_status=expected)
    user_results.append(ok)
    status = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
    print(f"  {status} {name:30} {method:6} {endpoint:35} {result}")

# Step 5: Verify User Data Structure
print(f"\n{BOLD}5. USER DATA VALIDATION{RESET}")
print("-" * 90)

try:
    users_resp = requests.get('http://localhost:8000/api/v1/users', headers=headers, timeout=5)
    if users_resp.status_code == 200:
        users = users_resp.json()
        print(f"  Total users in database: {len(users)}\n")
        
        for u in users:
            username = u.get('username', 'N/A')
            role = u.get('role', 'N/A')
            is_system = u.get('isSystemUser', u.get('is_system_user', False))
            
            # Validate structure
            has_id = 'id' in u
            has_username = 'username' in u
            has_role = 'role' in u
            has_system_flag = 'isSystemUser' in u or 'is_system_user' in u
            
            all_fields = has_id and has_username and has_role and has_system_flag
            field_status = f"{GREEN}✓{RESET}" if all_fields else f"{RED}✗{RESET}"
            
            system_indicator = f"{GREEN}[SYSTEM]{RESET}" if is_system else "[ORG]"
            
            print(f"  {field_status} {username:15} | {role:12} | {system_indicator}")
            
            if not all_fields:
                print(f"      Missing fields: ", end="")
                missing = []
                if not has_id: missing.append("id")
                if not has_username: missing.append("username")
                if not has_role: missing.append("role")
                if not has_system_flag: missing.append("isSystemUser")
                print(", ".join(missing))
    else:
        print(f"  {RED}Failed to fetch users: {users_resp.status_code}{RESET}")
except Exception as e:
    print(f"  {RED}Error validating users: {e}{RESET}")

# Step 6: Verify System Users
print(f"\n{BOLD}6. SYSTEM ADMINISTRATORS VERIFICATION{RESET}")
print("-" * 90)

try:
    users_resp = requests.get('http://localhost:8000/api/v1/users', headers=headers, timeout=5)
    if users_resp.status_code == 200:
        users = users_resp.json()
        system_users = [u for u in users if u.get('isSystemUser') or u.get('is_system_user')]
        
        print(f"  System users found: {len(system_users)}\n")
        
        if len(system_users) >= 2:
            print(f"  {GREEN}✓{RESET} Found at least 2 system administrators (required)")
        else:
            print(f"  {RED}✗{RESET} Expected at least 2 system administrators, found {len(system_users)}")
        
        for u in system_users:
            username = u.get('username', 'N/A')
            role = u.get('role', 'N/A')
            print(f"      • {username:15} ({role})")
except Exception as e:
    print(f"  {RED}Error checking system users: {e}{RESET}")

# Summary
print(f"\n{BOLD}SUMMARY{RESET}")
print("="*90)

total_tests = len(core_results) + len(user_results)
passed_tests = sum(core_results) + sum(user_results)

if passed_tests == total_tests:
    print(f"{GREEN}✓ ALL TESTS PASSED ({passed_tests}/{total_tests}){RESET}")
    print(f"\n{BOLD}Status: READY FOR FRONTEND TESTING{RESET}")
    print("\nYou can now:")
    print("  1. Open http://localhost:5173 in your browser")
    print("  2. Log in with: root / root")
    print("  3. Navigate to: System Settings → Access Control → System Administrators")
    print("  4. Verify that .amer and root are displayed without blinking")
else:
    print(f"{RED}✗ SOME TESTS FAILED ({passed_tests}/{total_tests}){RESET}")
    print(f"\n{BOLD}Issues found:{RESET}")
    print("Please review the failures above")

print("\n" + "="*90 + "\n")
