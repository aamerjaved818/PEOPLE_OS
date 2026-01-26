import os
import requests
import json

API_PORT = os.getenv("API_PORT", "8000")
BASE_URL = f"http://localhost:{API_PORT}"

def create_org():
    payload = {
        "name": "Test Organization",
        "code": "TEST-ORG-001",
        "email": "admin@testorg.com",
        "is_active": True
    }
    print(f"POST {BASE_URL}/api/organizations")
    try:
        # Assuming admin/admin123 or similar credential might be needed if secured, 
        # but the code in OrganizationManagement uses current user. 
        # For now, we try unauthenticated or we'll need a token.
        # Actually crud.create_organization uses user_id, so we need auth.
        
        # Login first
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "admin123"})
        token = None
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            print("Logged in successfully.")
        else:
            print("Login failed, trying without token (might fail).")

        headers = {"Authorization": f"Bearer {token}"} if token else {}
        resp = requests.post(f"{BASE_URL}/api/organizations", json=payload, headers=headers)
        print(f"Status: {resp.status_code}")
        print(resp.text)
        
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    create_org()
