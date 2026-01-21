import requests
import json

BASE_URL = "http://localhost:8000"

def get_orgs():
    print(f"GET {BASE_URL}/api/v1/organizations")
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/organizations")
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
