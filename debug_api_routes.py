import requests
import sys

BASE_URL = "http://localhost:8000"

paths_to_check = [
    "/api/v1/auth/login",
    "/api/v1/login",
    "/auth/login",
    "/api/auth/login",
    "/api/v1/auth/token",
    "/docs",  # Check if docs load (server is up)
]

print(f"Checking API connectivity on {BASE_URL}...")

try:
    # First check root/health
    resp = requests.get(f"{BASE_URL}/api/v1/health", timeout=3)
    print(f"Health Check (/api/v1/health): {resp.status_code}")
except Exception as e:
    print(f"Server seems down or unreachable: {e}")
    sys.exit(1)

print("\nProbing Login Routes (POST):")
for path in paths_to_check:
    url = f"{BASE_URL}{path}"
    try:
        # Send empty JSON to trigger 422 (Validation Error) or 401, implies route EXISTS
        # 404 = Route doesn't exist
        # 405 = Method not allowed (POST vs GET)
        if path == "/docs":
             resp = requests.get(url, timeout=1)
        else:
             resp = requests.post(url, json={}, timeout=1)
        
        status = resp.status_code
        print(f"[{status}] {url}")
        
        if status != 404:
            print(f"   >>> FOUND! Route is active at: {path}")
            
    except Exception as e:
        print(f"[ERR] {url}: {e}")
