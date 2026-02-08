import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
# Use Service Role Key to bypass RLS policies if necessary (standard for admin scripts)
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)

def create_event():
    now = datetime.now(timezone.utc)
    
    # "3 nights from tonight"
    # Assuming "tonight" is roughly now, + 3 days.
    # Set time to 7 PM (19:00) local? Or just +3 days same time.
    # Let's just do +3 days + rounds to hour for neatness
    event_date = now + timedelta(days=3)
    
    # "roster and reserver list signups already being accepted"
    # Means open times are in the past
    open_time = now - timedelta(days=1)
    
    # Scheduling windows usually happen later?
    # If "Reserve List" is accepted, we are likely in the Holding Phase (Window 1).
    # So initial scheduling (Window 2 start) is in future.
    initial_sched = now + timedelta(days=1)
    final_sched = now + timedelta(days=2)
    
    event_payload = {
        "name": f"Test Pickleball Night {event_date.strftime('%Y-%m-%d')}",
        "status": "SCHEDULED",
        "max_signups": 16, # Standard pickleball number
        "event_date": event_date.isoformat(),
        "roster_sign_up_open": open_time.isoformat(),
        "waitlist_sign_up_open": open_time.isoformat(), # Assuming same as roster for simplicity
        "reserve_sign_up_open": open_time.isoformat(),
        "initial_reserve_scheduling": initial_sched.isoformat(),
        "final_reserve_scheduling": final_sched.isoformat()
    }
    
    print("--- Creating Event ---")
    print(f"Name: {event_payload['name']}")
    print(f"Date: {event_payload['event_date']}")
    print(f"Signups Opened: {event_payload['roster_sign_up_open']}")
    
    try:
        res = supabase.table("events").insert(event_payload).execute()
        if res.data:
            new_event = res.data[0]
            print(f"\nSUCCESS: Created Event ID: {new_event['id']}")
            print("You can use this ID for testing signups.")
        else:
            print("Failed to create event (No data returned).")
            
    except Exception as e:
        print(f"Error creating event: {e}")

if __name__ == "__main__":
    create_event()
