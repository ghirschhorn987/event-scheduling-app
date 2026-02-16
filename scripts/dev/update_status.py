
import sys
import os
import requests
from dotenv import load_dotenv

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), '../../backend/.env'))

API_URL = "http://localhost:8000/api/schedule"
CRON_SECRET = os.environ.get("CRON_SECRET")

def update_status():
    print(f"Triggering Status Update via API: {API_URL}")
    
    headers = {
        "X-Cron-Secret": CRON_SECRET,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(API_URL, headers=headers)
        
        if response.status_code == 200:
            print("Success!")
            print(response.json())
        else:
            print(f"Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error connecting to API: {e}")
        print("Make sure the backend is running on localhost:8000")

if __name__ == "__main__":
    if not CRON_SECRET:
        print("Warning: CRON_SECRET not found in environment. Request might be unauthorized.")
    
    update_status()
