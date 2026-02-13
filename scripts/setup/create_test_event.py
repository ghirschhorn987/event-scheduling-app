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
    
    # Define Types
    types_data = [
        {
            "name": "Sunday Basketball",
            "day_of_week": 0, # Sunday
            "time_of_day": "19:00", # 7 PM
            "initial_reserve_scheduling_minutes": 360 # 6 hours (Override)
        },
        {
            "name": "Tuesday Basketball",
            "day_of_week": 2, # Tuesday
            "time_of_day": "20:00" # 8 PM
        },
        {
            "name": "Thursday Basketball",
            "day_of_week": 4, # Thursday
            "time_of_day": "20:00" # 8 PM
        }
    ]
    
    print("--- Creating Event Types ---")
    created_types = {}
    
    # Fetch Group IDs
    print("Fetching Group IDs...")
    groups_res = supabase.table("user_groups").select("id, name").execute()
    group_map = {g['name']: g['id'] for g in groups_res.data}
    
    first_priority_id = group_map.get("FirstPriority")
    second_priority_id = group_map.get("SecondPriority")
    
    if not first_priority_id or not second_priority_id:
        print("WARNING: Priority groups not found! Make sure to run migration/seed first.")

    for t_data in types_data:
        # Merge with defaults (defaults handled by DB, but we pass what we need)
        payload = {
            "name": t_data["name"],
            "day_of_week": t_data["day_of_week"],
            "time_of_day": t_data["time_of_day"],
            "time_zone": "America/Los_Angeles"
        }
        
        # Add overrides if present
        if "initial_reserve_scheduling_minutes" in t_data:
            payload["initial_reserve_scheduling_minutes"] = t_data["initial_reserve_scheduling_minutes"]
            
        # Add Group Restrictions
        # 1. Roster Group (Matches name of event type, e.g. "Sunday Basketball" -> "SundayBasketball" group?)
        # User requested: "roster_user_group point to user_group with name SundayBasketball"
        # The event type dict uses "Sunday Basketball" (with space).
        # The group name uses "SundayBasketball" (no space).
        
        roster_group_name = t_data["name"].replace(" ", "")
        roster_group_id = group_map.get(roster_group_name)
        
        if roster_group_id:
            payload["roster_user_group"] = roster_group_id
        else:
            print(f"Warning: Roster group '{roster_group_name}' not found for type '{t_data['name']}'")
            
        if first_priority_id:
            payload["reserve_first_priority_user_group"] = first_priority_id
            
        if second_priority_id:
            payload["reserve_second_priority_user_group"] = second_priority_id
            
        try:
            # Check if exists (by name) to avoid dupes in repeated runs
            existing = supabase.table("event_types").select("*").eq("name", t_data["name"]).execute()
            if existing.data:
                print(f"Type '{t_data['name']}' already exists. Updating groups...")
                # Update existing just in case
                update_payload = {}
                if roster_group_id: update_payload["roster_user_group"] = roster_group_id
                if first_priority_id: update_payload["reserve_first_priority_user_group"] = first_priority_id
                if second_priority_id: update_payload["reserve_second_priority_user_group"] = second_priority_id
                
                if update_payload:
                    supabase.table("event_types").update(update_payload).eq("id", existing.data[0]["id"]).execute()
                    
                created_types[t_data["name"]] = existing.data[0]["id"]
            else:
                res = supabase.table("event_types").insert(payload).execute()
                if res.data:
                    new_id = res.data[0]["id"]
                    print(f"Created '{t_data['name']}' with ID: {new_id}")
                    created_types[t_data["name"]] = new_id
        except Exception as e:
            print(f"Error creating/updating type '{t_data['name']}': {e}")

    # 2. Create Event Instances (One for each type, next 8 weeks)
    print("\n--- Creating Event Instances (Next 8 Weeks) ---")
    
    # Helper to find next occurrence of a weekday in the GIVEN TIMEZONE
    import pytz
    
    def get_next_occurrence(start_dt, target_weekday_py, hour, minute, tz_name):
        """
        Finds the next occurrence of a weekday/time in the specific timezone.
        Ensures 7 PM stays 7 PM even across DST boundaries.
        """
        tz = pytz.timezone(tz_name)
        
        # Convert start_dt to local time
        if start_dt.tzinfo is None:
            now_local = pytz.utc.localize(start_dt).astimezone(tz)
        else:
            now_local = start_dt.astimezone(tz)
            
        days_ahead = target_weekday_py - now_local.weekday()
        if days_ahead <= 0:
            days_ahead += 7
            
        next_day = now_local + timedelta(days=days_ahead)
        
        # Construct the target time on that day
        # We assume the event is at fixed local time (e.g. 19:00)
        target_local = tz.localize(datetime(
            next_day.year, next_day.month, next_day.day,
            hour, minute, 0
        ))
        
        return target_local

    for name, type_id in created_types.items():
        # Find the DOW for this type
        t_def = next(t for t in types_data if t["name"] == name)
        
        db_dow = t_def["day_of_week"]
        py_dow = 6 if db_dow == 0 else db_dow - 1
        
        t_str = t_def["time_of_day"] # "19:00"
        h, m = map(int, t_str.split(':'))
        tz_name = "America/Los_Angeles" # Or from t_def["time_zone"] if available
        
        # Find first occurrence
        first_event_local = get_next_occurrence(now, py_dow, h, m, tz_name)
        
        # Create for next 8 weeks
        # We must add 1 week at a time and RE-LOCALIZE to ensure DST is respected
        # (Simply adding timedelta(weeks=1) to a timezone-aware datetime usually handles it in pytz if using normalize, 
        # but safely constructing from year/month/day is robust)
        
        current_event_local = first_event_local
        
        for i in range(8):
            # To handle DST correctly when adding weeks, we should adding 7 days to the DATE and re-combining with TIME
            # Pytz's safe method:
            # But simpler here since we know the cycle:
            
            # Calculate target date
            target_date = first_event_local + timedelta(weeks=i)
            
            # Re-construct at 7 PM on that date in that TZ
            tz = pytz.timezone(tz_name)
            event_final = tz.localize(datetime(
                target_date.year, target_date.month, target_date.day,
                h, m, 0
            ))
            
            # Convert to ISO (which includes offset)
            # Supabase/Postgres TIMESTAMPTZ stores as UTC, but accepts ISO string with offset.
            
            payload = {
                "event_type_id": type_id,
                "event_date": event_final.isoformat(),
                "status": "SCHEDULED"
            }
            
            try:
                res = supabase.table("events").insert(payload).execute()
                if res.data:
                    # Print in local time implies success
                    print(f"Created '{name}' on {event_final.strftime('%Y-%m-%d %H:%M %Z')}")
            except Exception as e:
                # If duplicate (we re-ran script), just ignore
                if "duplicate key" in str(e):
                     print(f"Skipping '{name}' on {event_final.strftime('%Y-%m-%d')} (Already exists)")
                else:
                    print(f"Error creating event for '{name}': {e}")

if __name__ == "__main__":
    create_event()
