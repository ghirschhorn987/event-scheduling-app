import os
import requests
from dotenv import load_dotenv

load_dotenv("backend/.env")

BASE_URL = "http://localhost:8000"
CRON_SECRET = os.environ.get("CRON_SECRET", "test-secret")

def test_schedule_endpoint():
    print(f"Testing {BASE_URL}/api/schedule...")
    
    # 1. Test without header (Should Fail)
    print("\n1. Testing without header...")
    try:
        res = requests.post(f"{BASE_URL}/api/schedule")
        if res.status_code == 401:
            print("PASS: Request without header was rejected (401).")
        else:
            print(f"FAIL: Expected 401, got {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test with incorrect header (Should Fail)
    print("\n2. Testing with incorrect header...")
    try:
        res = requests.post(f"{BASE_URL}/api/schedule", headers={"X-Cron-Secret": "wrong-secret"})
        if res.status_code == 401:
            print("PASS: Request with wrong header was rejected (401).")
        else:
            print(f"FAIL: Expected 401, got {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

    # 3. Test with correct header (Should Succeed - or at least pass auth)
    # Note: Logic might fail if DB is not connected or empty, but we check status code != 401.
    print(f"\n3. Testing with correct header (Secret: {CRON_SECRET})...")
    try:
        res = requests.post(f"{BASE_URL}/api/schedule", headers={"X-Cron-Secret": CRON_SECRET})
        if res.status_code == 200:
            print("PASS: Request with correct header succeeded (200).")
            print(res.json())
        elif res.status_code != 401:
             print(f"PASS: Auth succeeded, but endpoint returned {res.status_code} (Logic error or DB issue, which is expected effectively).")
             print(res.text)
        else:
             print(f"FAIL: Request with correct header was rejected (401).")
    except Exception as e:
         print(f"Error: {e}")

if __name__ == "__main__":
    test_schedule_endpoint()
