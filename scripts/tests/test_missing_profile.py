import requests
from supabase import create_client
import os
from dotenv import load_dotenv
import uuid
import time

load_dotenv("backend/.env")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def run():
    print("--- 1. Fetching Events ---")
    events = supabase.table("events").select("*").execute()
    if not events.data:
        print("No events found!")
        return
    event_id = events.data[0]['id']
    print(f"Using Event ID: {event_id}")

    # Generate a random user ID that definitely doesn't exist
    user_id = str(uuid.uuid4())
    print(f"\n--- 2. Testing Signup with New User ID: {user_id} ---")
    
    # We need a token now. For this test script, we can mock it or we expect 401/403 if we don't present one.
    # To TRULY test the "Missing Profile" fix, we need to bypass the 401 check or have a valid token.
    # Since we can't easily generate a valid Supabase JWT without the secret, 
    # we'll use a mocked "Authorization" header if we were in a test env, 
    # OR we rely on the Manual Verification steps where the User logs in via Frontend.
    
    # However, to verify the STATUS of the fix via script:
    # Let's try to send a headers dictionary.
    
    # NOTE: This script will likely fail with 401 now because we don't have a real token.
    # This actually CONFIRMS we secured the endpoint!
    payload = {
        "event_id": event_id,
        "user_id": user_id
    }
    
    headers = {
        # "Authorization": "Bearer <INSERT_VALID_TOKEN_IF_KNOWN>" 
    }
    
    try:
        res = requests.post("http://localhost:8000/api/signup", json=payload, headers=headers)
        print(f"Status Code: {res.status_code}")
        print(f"Response Text: {res.text}")
        
    except Exception as e:
        print(f"Request failed: {e}")

    # Check if profile was created
    print("\n--- 3. Verifying Profile Creation ---")
    try:
        profile = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if profile.data:
            print("SUCCESS: Profile was created!")
            print(profile.data)
        else:
            print("FAILURE: Profile was NOT created.")
    except Exception as e:
        print(f"Error checking profile: {e}")

if __name__ == "__main__":
    run()
