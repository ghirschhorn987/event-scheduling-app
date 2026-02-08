import requests
import json
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

BASE_URL = "http://localhost:8000"
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")  # Anon Key
AUTH_URL = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"

# Load Mock Users
with open("frontend/src/mock_users.json", "r") as f:
    MOCK_USERS = json.load(f)

# Hardcoded Event ID (from previous step)
EVENT_ID = "50b2d733-40f3-4011-9a77-50c15482c057"

def login(email, password="password123"): # Default password from create script
    payload = {"email": email, "password": password}
    headers = {"apikey": SUPABASE_KEY}
    res = requests.post(AUTH_URL, json=payload, headers=headers)
    if res.status_code != 200:
        print(f"Login Failed for {email}: {res.text}")
        return None
    return res.json()

def signup(token, user_id, event_id):
    url = f"{BASE_URL}/api/signup"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"event_id": event_id, "user_id": user_id}
    res = requests.post(url, json=payload, headers=headers)
    return res

def remove(token, user_id, event_id):
    # Mimic Frontend: Direct Delete via REST
    # URL: /rest/v1/event_signups?event_id=eq.X&user_id=eq.Y
    url = f"{SUPABASE_URL}/rest/v1/event_signups?event_id=eq.{event_id}&user_id=eq.{user_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    res = requests.delete(url, headers=headers)
    return res

def test_user_flow(role_name, user_obj):
    print(f"\n--- Testing Flow: {role_name} ({user_obj['email']}) ---")
    
    # 1. Login
    auth = login(user_obj['email'])
    if not auth: return
    token = auth['access_token']
    
    # 2. Add Name
    print("Action: Add My Name")
    s_res = signup(token, user_obj['id'], EVENT_ID)
    if s_res.status_code == 200:
        data = s_res.json().get('data', {})
        print(f"  -> Success. List: {data.get('list_type')} | Seq: {data.get('sequence_number')}")
    else:
        print(f"  -> Failed: {s_res.status_code} {s_res.text}")
        
    # 3. Remove Name
    print("Action: Remove My Name")
    r_res = remove(token, user_obj['id'], EVENT_ID)
    if r_res.status_code == 204:
        print("  -> Success (204 No Content)")
    else:
        print(f"  -> Failed: {r_res.status_code} {r_res.text}")

def test_capacity():
    print(f"\n--- Testing Capacity (Filling 16 spots) ---")
    
    # We need 17 users. 
    # MOCK_USERS has 15 primaries, 10 secondaries.
    # We'll use Primaries 1-15 + Secondary 1 for roster, Secondary 2 for Overflow.
    
    roster_users = [u for u in MOCK_USERS if u['role'] == 'primary'][:15]
    roster_users.append([u for u in MOCK_USERS if u['role'] == 'secondary'][0]) # 16th user
    
    overflow_user = [u for u in MOCK_USERS if u['role'] == 'secondary'][1] # 17th user
    
    print(f"Target: {len(roster_users)} signups to fill roster.")
    
    for i, user in enumerate(roster_users):
        auth = login(user['email'])
        if not auth: continue
        
        res = signup(auth['access_token'], user['id'], EVENT_ID)
        if res.status_code == 200:
            d = res.json()['data']
            print(f"User {i+1} ({user['role']}): {d['list_type']} #{d['sequence_number']}")
        else:
            print(f"User {i+1} Failed: {res.text}")
            
    print("\n--- Try Adding 17th User (Should go to WAITLIST) ---")
    auth = login(overflow_user['email'])
    res = signup(auth['access_token'], overflow_user['id'], EVENT_ID)
    if res.status_code == 200:
        d = res.json()['data']
        print(f"Result: {d['list_type']} #{d['sequence_number']}")
        if d['list_type'] == 'WAITLIST':
            print("SUCCESS: 17th user went to Waitlist.")
        else:
            print(f"FAILURE: Expected WAITLIST, got {d['list_type']}")
    else:
        print(f"Request Failed: {res.text}")

def run():
    # 1. Test Individual Flows
    primary = next(u for u in MOCK_USERS if u['role'] == 'primary')
    secondary = next(u for u in MOCK_USERS if u['role'] == 'secondary')
    guest = next(u for u in MOCK_USERS if u['role'] == 'guest')
    
    test_user_flow("Primary", primary)
    test_user_flow("Secondary", secondary)
    test_user_flow("Guest", guest)
    
    # 2. Test Capacity
    # Note: The above tests added/removed, so the event should be empty now.
    # Wait, did we handle cleanup properly? Yes, test_user_flow removes at the end.
    test_capacity()

if __name__ == "__main__":
    run()
