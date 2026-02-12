
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

def check_user(email):
    print(f"\n--- Checking User: {email} ---")
    # Get Profile
    res = supabase.table("profiles").select("*, profile_groups(user_groups(name))").eq("email", email).execute()
    if not res.data:
        print("User not found in 'profiles' table.")
        return
    
    user = res.data[0]
    print(f"Profile ID: {user['id']}")
    print(f"Name: {user['name']}")
    
    groups = []
    if user.get("profile_groups"):
        groups = [pg['user_groups']['name'] for pg in user['profile_groups'] if pg.get('user_groups')]
    
    print(f"Groups: {groups}")
    return groups

def check_next_event():
    print("\n--- Checking Next Event ---")
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    
    res = supabase.table("events").select("*, event_types(*)").gt("event_date", now).order("event_date").limit(1).execute()
    
    if not res.data:
        print("No upcoming events found.")
        return
        
    event = res.data[0]
    print(f"Event: {event.get('event_types', {}).get('name')}")
    print(f"Date: {event['event_date']}")
    print(f"Status: {event['status']}")
    
    et = event.get('event_types', {})
    print(f"Roster Group: {et.get('roster_user_group')}")
    print(f"Tier 1 (First Priority): {et.get('reserve_first_priority_user_group')}")
    print(f"Tier 2 (Second Priority): {et.get('reserve_second_priority_user_group')}")

    return event

if __name__ == "__main__":
    u1_groups = check_user("ghirschhorn987@gmail.com")
    u2_groups = check_user("test2@skeddle.club")
    
    check_next_event()
