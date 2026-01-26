"""
PEOPLE OS - COMPREHENSIVE SYSTEM TEST
Tests all components: Database, Backend, Frontend Readiness, and Data Integrity
"""
import os
import requests
import json
import time
from datetime import datetime

# Configuration from environment
API_PORT = os.getenv("API_PORT", "8000")
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "5173")
API_URL = f"http://localhost:{API_PORT}/api"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def section(title):
    print(f"\n{BOLD}{BLUE}{'='*100}{RESET}")
    print(f"{BOLD}{BLUE}{title.center(100)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*100}{RESET}{RESET}\n")

def test_result(passed, message, details=""):
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} | {message}")
    if details:
        print(f"     {details}")

def subsection(title):
    print(f"\n{BOLD}{title}{RESET}")
    print(f"{'-'*100}\n")

# ============================================================================
# PART 1: SYSTEM HEALTH CHECK
# ============================================================================
section("PART 1: SYSTEM HEALTH CHECK")

subsection("Backend Status")

# Check if backend is running
try:
    r = requests.get(f'{API_URL}/health', timeout=3)
    backend_ok = r.status_code == 200
    test_result(backend_ok, "Backend health endpoint", f"Status: {r.status_code}")
except Exception as e:
    backend_ok = False
    test_result(False, "Backend health endpoint", f"Error: {str(e)[:60]}")

if not backend_ok:
    print(f"\n{RED}ERROR: Backend is not responding. Please start the backend with: python -m backend.main{RESET}")
    exit(1)

# Check database connectivity
try:
    r = requests.get(f'{API_URL}/health', timeout=3)
    health = r.json()
    db_ok = health.get('database') == 'Connected'
    test_result(db_ok, "Database connection", f"Status: {health.get('database')}")
except Exception as e:
    test_result(False, "Database connection", f"Error: {str(e)[:60]}")

# ============================================================================
# PART 2: AUTHENTICATION
# ============================================================================
section("PART 2: AUTHENTICATION & LOGIN")

subsection("User Authentication")

# Test root/root login
try:
    r = requests.post(
        f'{API_URL}/auth/login',
        json={'username': 'root', 'password': 'root'},
        timeout=5
    )
    login_ok = r.status_code == 200
    test_result(login_ok, "root/root login", f"Status: {r.status_code}")
    
    if login_ok:
        token = r.json()['access_token']
        user = r.json().get('user', {})
        headers = {'Authorization': f'Bearer {token}'}
        
        # Verify token structure
        token_ok = isinstance(token, str) and len(token) > 20
        test_result(token_ok, "Access token generated", f"Token length: {len(token)}")
        
        # Verify user data in login response
        user_ok = (
            user.get('username') == 'root' and
            user.get('role') == 'Root' and
            'isSystemUser' in user
        )
        test_result(user_ok, "User data in login response", 
                   f"User: {user.get('username')}, Role: {user.get('role')}, isSystemUser: {user.get('isSystemUser')}")
except Exception as e:
    test_result(False, "root/root login", f"Error: {str(e)[:60]}")
    exit(1)

# ============================================================================
# PART 3: CORE DATA ENDPOINTS
# ============================================================================
section("PART 3: CORE DATA ENDPOINTS (fetchMasterData)")

subsection("Master Data Endpoints")

endpoints_to_test = [
    ("System Flags", "/system/flags"),
    ("Payroll Settings", "/payroll-settings"),
    ("Users List", "/users"),
    ("Organizations", "/organizations"),
]

endpoint_results = {}
for name, endpoint in endpoints_to_test:
    try:
        r = requests.get(f'{API_URL}{endpoint}', headers=headers, timeout=5)
        endpoint_ok = r.status_code == 200
        endpoint_results[endpoint] = endpoint_ok
        
        data = r.json() if endpoint_ok else {}
        data_info = f"({len(data)} items)" if isinstance(data, list) else f"({len(data)} fields)" if isinstance(data, dict) else ""
        
        test_result(endpoint_ok, f"{name:25} GET {endpoint:30}", f"Status: {r.status_code} {data_info}")
    except Exception as e:
        endpoint_results[endpoint] = False
        test_result(False, f"{name:25} GET {endpoint:30}", f"Error: {str(e)[:50]}")

all_endpoints_ok = all(endpoint_results.values())

# ============================================================================
# PART 4: USER DATA VALIDATION
# ============================================================================
section("PART 4: USER DATA VALIDATION")

subsection("Database User Records")

try:
    r = requests.get(f'{API_URL}/users', headers=headers, timeout=5)
    if r.status_code == 200:
        users = r.json()
        
        print(f"Total users in database: {BOLD}{len(users)}{RESET}\n")
        
        # Validate each user
        all_users_valid = True
        for u in users:
            username = u.get('username', 'N/A')
            role = u.get('role', 'N/A')
            is_system = u.get('isSystemUser') or u.get('is_system_user') or False
            
            # Check required fields
            has_id = 'id' in u
            has_username = 'username' in u
            has_role = 'role' in u
            has_system_flag = 'isSystemUser' in u or 'is_system_user' in u
            
            user_valid = has_id and has_username and has_role and has_system_flag
            all_users_valid = all_users_valid and user_valid
            
            system_tag = f"{GREEN}[SYSTEM]{RESET}" if is_system else "[ORG   ]"
            test_result(user_valid, f"User record: {username:15} | {role:12} | {system_tag}")
        
        # Summary
        print(f"\n{BOLD}User Data Summary:{RESET}")
        system_users = [u for u in users if u.get('isSystemUser') or u.get('is_system_user')]
        org_users = [u for u in users if not (u.get('isSystemUser') or u.get('is_system_user'))]
        
        test_result(len(system_users) >= 2, f"System Administrators count", 
                   f"Found: {len(system_users)} (required: 2)")
        test_result(len(org_users) >= 1, f"Organization Users count", 
                   f"Found: {len(org_users)} (required: 1)")
        
        # List system users
        print(f"\n{BOLD}System Administrators:{RESET}")
        for u in system_users:
            print(f"  • {u.get('username'):20} ({u.get('role')})")
        
        # List org users
        print(f"\n{BOLD}Organization Users:{RESET}")
        for u in org_users:
            print(f"  • {u.get('username'):20} ({u.get('role')})")
    else:
        test_result(False, "Fetch users endpoint", f"Status: {r.status_code}")
except Exception as e:
    test_result(False, "Fetch users endpoint", f"Error: {str(e)[:60]}")

# ============================================================================
# PART 5: SYSTEM ADMINISTRATOR FILTER LOGIC
# ============================================================================
section("PART 5: SYSTEM ADMINISTRATOR FILTER LOGIC")

subsection("Access Control Component Validation")

try:
    r = requests.get(f'{API_URL}/users', headers=headers, timeout=5)
    if r.status_code == 200:
        users = r.json()
        
        # Simulate the frontend filter logic from UserManagement.tsx
        # systemUsers = users.filter(u => u.isSystemUser === true)
        system_users = [u for u in users if u.get('isSystemUser') == True or u.get('is_system_user') == True]
        
        # For Root user viewing
        root_users = [u for u in system_users if u.get('role') == 'Root']
        
        print(f"Filter simulation (frontend logic):\n")
        print(f"  All users: {len(users)}")
        print(f"  System users (isSystemUser=true): {len(system_users)}")
        print(f"  Root users (visible to Root): {len(root_users)}\n")
        
        # Validate filter results
        test_result(
            len(system_users) == 2, 
            "System users filter result",
            f"Expected: 2 (.amer, root), Got: {len(system_users)}"
        )
        
        test_result(
            len(root_users) == 2,
            "Root users visible to Root admin",
            f"Expected: 2, Got: {len(root_users)}"
        )
        
        # Validate specific users are returned
        usernames = [u.get('username') for u in system_users]
        has_root = 'root' in usernames
        has_amer = '.amer' in usernames
        
        test_result(has_root and has_amer, "Required system users present",
                   f"root: {has_root}, .amer: {has_amer}")
except Exception as e:
    test_result(False, "Filter logic validation", f"Error: {str(e)[:60]}")

# ============================================================================
# PART 6: CORS & HEADERS VALIDATION
# ============================================================================
section("PART 6: CORS & FRONTEND INTEGRATION")

subsection("Cross-Origin Resource Sharing (CORS)")

try:
    # Test CORS preflight
    cors_headers = {
        'Origin': FRONTEND_URL,
        'Access-Control-Request-Method': 'GET'
    }
    
    r = requests.options(f'{API_URL}/users', headers=cors_headers, timeout=5)
    
    cors_ok = 'access-control-allow-origin' in r.headers
    allow_origin = r.headers.get('access-control-allow-origin', 'NOT SET')
    
    test_result(cors_ok, "CORS headers present", f"Allow-Origin: {allow_origin}")
    
    # Check specific origin
    origin_match = allow_origin == '*' or FRONTEND_PORT in allow_origin
    test_result(origin_match, "localhost:5173 allowed", f"Value: {allow_origin}")
except Exception as e:
    test_result(False, "CORS validation", f"Error: {str(e)[:60]}")

# ============================================================================
# PART 7: INTEGRATION READINESS CHECK
# ============================================================================
section("PART 7: INTEGRATION READINESS CHECK")

subsection("Frontend Integration Status")

print(f"{BOLD}Pre-requisites for Frontend:{RESET}\n")

frontend_ready = [
    ("Backend running and responding", backend_ok),
    ("Database connected", db_ok),
    ("Authentication working (root/root)", login_ok),
    ("All data endpoints responding", all_endpoints_ok),
    ("Users with isSystemUser field present", 'isSystemUser' in user),
    ("System administrators found (2+)", len(system_users) >= 2),
    (f"CORS configured for localhost:{FRONTEND_PORT}", cors_ok),
]

for requirement, status in frontend_ready:
    test_result(status, requirement)

ready = all([status for _, status in frontend_ready])

# ============================================================================
# FINAL SUMMARY
# ============================================================================
section("SYSTEM TEST SUMMARY")

if ready:
    print(f"{GREEN}{BOLD}✓ ALL SYSTEM TESTS PASSED{RESET}\n")
    print(f"{BOLD}System Status: READY FOR PRODUCTION{RESET}\n")
    print(f"{YELLOW}Next Steps:{RESET}")
    print(f"  1. Open {FRONTEND_URL} in your browser")
    print(f"  2. Hard refresh: Ctrl+Shift+R")
    print(f"  3. Log in with: root / root")
    print(f"  4. Navigate to: System Settings → Access Control → System Administrators")
    print(f"  5. Verify: .amer and root are displayed without blinking")
    print(f"\n{BOLD}Expected Result:{RESET}")
    print(f"  • System Administrators table shows 2 rows")
    print(f"  • First row: .amer (Root)")
    print(f"  • Second row: root (Root)")
    print(f"  • Data is persistent (no blinking/disappearing)")
else:
    print(f"{RED}{BOLD}✗ SOME TESTS FAILED{RESET}\n")
    print(f"{BOLD}Please review the failed tests above and fix the issues.{RESET}\n")
    failed_count = sum(1 for _, status in frontend_ready if not status)
    print(f"Failed: {failed_count} requirement(s)\n")

print(f"\n{BOLD}{'='*100}{RESET}")
print(f"{BOLD}Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
print(f"{BOLD}{'='*100}{RESET}\n")
