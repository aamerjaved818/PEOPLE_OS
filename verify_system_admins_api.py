
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"
ROOT_USERNAME = "root"
ROOT_PASSWORD = "root"  # Default dev password

def test_system_admins():
    print(f"[-] Logging in as {ROOT_USERNAME}...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "username": ROOT_USERNAME,
            "password": ROOT_PASSWORD
        })
        if resp.status_code != 200:
            print(f"[!] Login failed: {resp.text}")
            return False
            
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[+] Login successful.")
        
        print(f"[-] Fetching users list...")
        resp = requests.get(f"{BASE_URL}/users", headers=headers)
        if resp.status_code != 200:
             print(f"[!] Update failed: {resp.text}")
             return False
        
        users = resp.json()
        print(f"[+] Retrieved {len(users)} users.")
        
        # Check for Root
        root_found = any(u["username"] == "root" for u in users)
        amer_found = any(u["username"] == "amer" for u in users)
        
        if root_found:
            print("[PASS] User 'root' found in list.")
        else:
            print("[FAIL] User 'root' NOT found in list.")
            
        if amer_found:
            print("[PASS] User 'amer' found in list.")
        else:
            print("[FAIL] User 'amer' NOT found in list.")
            
        if root_found and amer_found:
            print("\n[SUCCESS] System Administrators are visible.")
            return True
        else:
            return False

    except Exception as e:
        print(f"[!] Error: {e}")
        return False

if __name__ == "__main__":
    success = test_system_admins()
    sys.exit(0 if success else 1)
