import os
import requests
import json

API_PORT = os.getenv("API_PORT", "8000")
BASE_URL = f"http://localhost:{API_PORT}"

def get_orgs():
    print(f"GET {BASE_URL}/api/organizations")
    try:
        resp = requests.get(f"{BASE_URL}/api/organizations")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(json.dumps(data, indent=2))
        else:
            print(resp.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    get_orgs()
