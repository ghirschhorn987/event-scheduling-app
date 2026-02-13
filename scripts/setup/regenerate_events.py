import os
from datetime import datetime, timedelta, timezone
import pytz
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in backend/.env")

supabase: Client = create_client(url, key)

def regenerate_events():
    print("--- Regenerating Events ---")
    
    # 1. Delete existing signups and events
    print("Deleting existing signups...")
    # Fetch all signups and delete them.
    # Note: If ON DELETE CASCADE is set, deleting events might be enough, but let's be safe.
    try:
         # Limit is required for delete without where, but we want to delete all.
         # So we select all IDs first.
         res = supabase.table("event_signups").select("id").execute()
         if res.data:
             ids = [r['id'] for r in res.data]
             # Delete in chunks if necessary, but for now assuming small dataset
             supabase.table("event_signups").delete().in_("id", ids).execute()
             print(f"Deleted {len(ids)} signups.")
         else:
             print("No signups found.")
    except Exception as e:
        print(f"Error deleting signups: {e}")

    print("Deleting existing events...")
    try:
        res = supabase.table("events").select("id").execute()
        if res.data:
            ids = [r['id'] for r in res.data]
            supabase.table("events").delete().in_("id", ids).execute()
            print(f"Deleted {len(ids)} events.")
        else:
            print("No events found.")
    except Exception as e:
        print(f"Error deleting events: {e}")

    # 2. Define Event Types
    # Check if they exist first, or just assume they do (from create_mock_users / create_test_event)
    # We need their IDs.
    
    # Expected Types
    target_types = {
        "Sunday Basketball": {"dow": 0, "time": "19:00"},
        "Tuesday Basketball": {"dow": 2, "time": "20:00"},
        "Thursday Basketball": {"dow": 4, "time": "20:00"}
    }
    
    type_ids = {}
    
    print("\nFetching Event Types...")
    for name in target_types:
        try:
            res = supabase.table("event_types").select("*").eq("name", name).execute()
            if res.data:
                type_ids[name] = res.data[0]['id']
                print(f"Found '{name}': {type_ids[name]}")
            else:
                print(f"WARNING: Event Type '{name}' not found! Skipping.")
        except Exception as e:
            print(f"Error fetching type '{name}': {e}")
            
    if not type_ids:
        print("No event types found. Aborting.")
        return

    # 3. Generate Events
    start_date = datetime(2026, 2, 11) # Feb 11, 2026
    # Note: datetime() creates a naive datetime. We'll localize it later or just use it as reference date.
    
    # We want 3 weeks of events.
    weeks_to_generate = 3
    
    tz_name = "America/Los_Angeles"
    local_tz = pytz.timezone(tz_name)
    
    print(f"\nGenerating events for {weeks_to_generate} weeks starting {start_date.date()}...")
    
    new_events_count = 0
    
    for name, type_info in target_types.items():
        if name not in type_ids: continue
        
        tid = type_ids[name]
        target_dow = type_info["dow"]
        target_time_str = type_info["time"]
        h, m = map(int, target_time_str.split(':'))
        
        # Calculate occurrences
        # Find first occurrence ON OR AFTER start_date matching this DOW
        
        # Start searching from start_date
        current_date = start_date
        
        # Python's datetime.weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6.
        # DB stores: Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6
        # So:
        # DB 0 (Sun) -> Py 6
        # DB 2 (Tue) -> Py 1
        # DB 4 (Thu) -> Py 3
        
        db_dow = target_dow
        py_dow = 6 if db_dow == 0 else db_dow - 1
        
        # Adjust current_date to first match
        # current_date is naive 2/11/2026 (Wednesday) = Py 2
        
        days_ahead = py_dow - current_date.weekday()
        if days_ahead < 0:
            days_ahead += 7
            
        first_match_date = current_date + timedelta(days=days_ahead)
        
        # Generate 3 weeks worth (0, 1, 2)
        for w in range(weeks_to_generate):
            event_date = first_match_date + timedelta(weeks=w)
            
            # Construct localized datetime
            # We want it to be at the specific time in LA time
            
            dt_local = local_tz.localize(datetime(
                event_date.year, event_date.month, event_date.day,
                h, m, 0
            ))
            
            # Convert to ISO for DB
            iso_str = dt_local.isoformat()
            
            try:
                payload = {
                    "event_type_id": tid,
                    "event_date": iso_str,
                    "status": "SCHEDULED"
                }
                res = supabase.table("events").insert(payload).execute()
                if res.data:
                    print(f"Created '{name}' on {dt_local.strftime('%Y-%m-%d %H:%M %Z')}")
                    new_events_count += 1
            except Exception as e:
                print(f"Error creating event: {e}")

    print(f"\nDone. Created {new_events_count} events.")

if __name__ == "__main__":
    regenerate_events()
