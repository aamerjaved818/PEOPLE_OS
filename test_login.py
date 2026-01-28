import requests
import json

def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    payload = {"username": "root", "password": "root"}
    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
