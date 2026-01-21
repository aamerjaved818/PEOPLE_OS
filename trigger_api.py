import requests
import sys

try:
    response = requests.get(url = "http://localhost:8001/api/v1/employees/ENERGY01-0001")
    if response.status_code == 200:
        print("API Call Successful")
        print(response.json())
    else:
        print(f"API Call Failed with status: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
