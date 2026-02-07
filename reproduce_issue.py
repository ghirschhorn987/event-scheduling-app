import requests
from supabase import create_client
import os
from dotenv import load_dotenv
import json

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

    print("\n--- 2. Fetching Profiles ---")
    profiles = supabase.table("profiles").select("*").execute()
    if not profiles.data:
        print("No profiles found! This confirms the missing profile issue.")
        # We need a user ID to test. If no profiles, we can't fully test the endpoint logic 
        # unless we know a user ID from somewhere else (like creating a fake one)
        # But let's try with a dummy ID to see if it hits the "Profile not found" 400 error vs 500.
        import uuid
        user_id = str(uuid.uuid4())
        print(f"Generated Random User ID for testing: {user_id}")
    else:
        user_id = profiles.data[0]['id']
        print(f"Using Existing User ID: {user_id} (This might not trigger the missing profile case)")

    print(f"\n--- 3. Testing Signup Endpoint for User {user_id} ---")
    payload = {
        "event_id": event_id,
        "user_id": user_id
    }
    
    try:
        res = requests.post("http://localhost:8000/api/signup", json=payload)
        print(f"Status Code: {res.status_code}")
        try:
            print("Response JSON:", res.json())
        except:
            print("Response Text:", res.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    run()
