import sys
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv("backend/.env")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Service Role for cleanup
BASE_URL = "http://localhost:8000"

EVENT_ID = "50b2d733-40f3-4011-9a77-50c15482c057"

with open("frontend/src/mock_users.json", "r") as f:
    MOCK_USERS = json.load(f)

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

def clear_signups():
    print(f"Clearing signups for event {EVENT_ID}...")
    url = f"{SUPABASE_URL}/rest/v1/event_signups?event_id=eq.{EVENT_ID}"
    res = requests.delete(url, headers=get_headers())
    if res.status_code in [200, 204]:
        print("SUCCESS: Event cleared.")
    else:
        print(f"FAILED: {res.status_code} {res.text}")

def login_user(email):
    # We need to login to get a valid token for the /api/signup endpoint
    # Use the Anon Key for auth
    anon_key = os.environ.get("SUPABASE_KEY")
    auth_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    res = requests.post(auth_url, json={"email": email, "password": "password123"}, headers={"apikey": anon_key})
    if res.status_code == 200:
        return res.json()['access_token']
    return None

def fill_signups(count=15):
    print(f"Filling event with {count} users...")
    
    # Get Primaries first
    users = [u for u in MOCK_USERS if u['role'] == 'primary'][:count]
    
    for i, user in enumerate(users):
        print(f"Adding User {i+1}: {user['email']}")
        token = login_user(user['email'])
        if not token:
            print(f"  -> Login Failed")
            continue
            
        url = f"{BASE_URL}/api/signup"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"event_id": EVENT_ID, "user_id": user['id']}
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code != 200:
            print(f"  -> Signup Failed: {res.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage_signups.py [clear|fill]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "clear":
        clear_signups()
    elif cmd == "fill":
        fill_signups(15)
    else:
        print("Unknown command")
