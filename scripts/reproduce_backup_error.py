import requests

BASE_URL = "http://localhost:8000"

# 1. Login to get token (assuming generic admin credentials, or we test without auth first)
def login(username, password):
    try:
        resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"username": username, "password": password})
        if resp.status_code == 200:
            return resp.json()["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
    return None

def test_backup_create(token):
    print("\nTesting Create Backup...")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        # Trying the likely endpoint for creating backup
        resp = requests.post(f"{BASE_URL}/api/v1/system/maintenance/backups", headers=headers)
        print(f"POST /api/v1/system/maintenance/backups Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Request failed: {e}")

def test_restore_auth(token):
    print("\nTesting Restore permissions...")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        # Trying to restore (dummy filename)
        resp = requests.post(f"{BASE_URL}/api/v1/system/maintenance/restore/dummy.bak", headers=headers)
        print(f"POST /api/v1/system/maintenance/restore/dummy.bak Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Test with no token first
    print("--- Testing without Auth ---")
    test_backup_create(None)
    test_restore_auth(None)
    
    # login as a known user (if we knew one, otherwise we skip or rely on previous knowledge)
    # derived from previous context: 'admin' / 'admin123' might be default
    token = login("admin", "admin123") 
    if token:
        print("\n--- Testing with 'admin' Auth ---")
        test_backup_create(token)
        test_restore_auth(token)
    else:
        print("\nCould not log in as 'admin' to test auth paths.")
