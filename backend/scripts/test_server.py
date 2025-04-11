import requests

BASE_URL = "http://localhost:5002"

try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Server is running correctly")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Server returned non-200 status code: {response.status_code}")
        print(f"Response text: {response.text}")
except Exception as e:
    print(f"❌ Error connecting to server: {str(e)}") 