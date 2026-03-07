import os
from datetime import datetime, timedelta, timezone
import pytz
from dotenv import load_dotenv
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
from db import supabase

def populate_future_events():
    print("--- Populating Future Events ---")
    
    # 1. Provide Event Types mapping
    # Determine what types exist in DB to fetch them dynamically rather than hardcoding names
    print("Fetching Event Types...")
    try:
        res = supabase.table("event_types").select("*").execute()
        if not res.data:
            print("No event types found. Aborting.")
            return
        
        event_types = res.data
        for t in event_types:
            print(f"Found event type: {t['name']} (DOW: {t['day_of_week']}, Time: {t['time_of_day']})")
    except Exception as e:
        print(f"Error fetching event types: {e}")
        return

    # 2. Generate Events
    # Start from today
    start_date = datetime.now()
    
    # Generate for the next 4 weeks
    weeks_to_generate = 4
    
    tz_name = "America/Los_Angeles"
    local_tz = pytz.timezone(tz_name)
    
    print(f"\nGenerating events for {weeks_to_generate} weeks starting {start_date.date()}...")
    
    new_events_count = 0
    
    for t in event_types:
        tid = t["id"]
        name = t["name"]
        db_dow = t["day_of_week"]
        target_time_str = t["time_of_day"]
        
        # Parse time (expected format "HH:MM:SS" or "HH:MM" etc.)
        time_parts = target_time_str.split(':')
        h = int(time_parts[0])
        m = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        # Python's datetime.weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6.
        # DB stores: Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6
        py_dow = 6 if db_dow == 0 else db_dow - 1
        
        days_ahead = py_dow - start_date.weekday()
        if days_ahead < 0:
             days_ahead += 7
            
        first_match_date = start_date + timedelta(days=days_ahead)
        
        for w in range(weeks_to_generate):
            event_date = first_match_date + timedelta(weeks=w)
            
            # Localize datetime
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
                    "status": "NOT_YET_OPEN" # Explicitly NOT_YET_OPEN to allow standard lifecycle
                }
                # Check if it already exists to avoid exact duplicates
                existing = supabase.table("events").select("id").eq("event_type_id", tid).eq("event_date", iso_str).execute()
                if not existing.data:
                    res = supabase.table("events").insert(payload).execute()
                    if res.data:
                        print(f"Created '{name}' on {dt_local.strftime('%Y-%m-%d %H:%M %Z')}")
                        new_events_count += 1
                else:
                    print(f"Skipping '{name}' on {dt_local.strftime('%Y-%m-%d %H:%M %Z')} (already exists)")
            except Exception as e:
                print(f"Error creating event: {e}")

    print(f"\nDone. Created {new_events_count} events.")

if __name__ == "__main__":
    populate_future_events()
