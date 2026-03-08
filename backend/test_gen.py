import sys
import os
import pytz
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db import supabase

try:
    res = supabase.table("event_types").select("*").execute()
    print(f"DEBUG: Found {len(res.data)} event types.")
    
    start_date = datetime.now()
    tz_name = "America/Los_Angeles"
    local_tz = pytz.timezone(tz_name)
    
    for t in res.data:
        tid = t["id"]
        db_dow = t["day_of_week"]
        target_time_str = t["time_of_day"]
        
        time_parts = target_time_str.split(':')
        h = int(time_parts[0])
        m = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        py_dow = 6 if db_dow == 0 else db_dow - 1
        days_ahead = py_dow - start_date.weekday()
        if days_ahead < 0:
             days_ahead += 7
            
        first_match_date = start_date + timedelta(days=days_ahead)
        
        print(f"DEBUG: Processing Type: {t['name']} (DOW {db_dow}), First match: {first_match_date.date()}")
        
        for w in range(4):
            event_date = first_match_date + timedelta(weeks=w)
            dt_local = local_tz.localize(datetime(
                event_date.year, event_date.month, event_date.day,
                h, m, 0
            ))
            iso_str = dt_local.isoformat()
            
            existing = supabase.table("events").select("id").eq("event_type_id", tid).eq("event_date", iso_str).execute()
            if existing.data:
                print(f"  Week {w}: Event already exists for {iso_str}")
            else:
                print(f"  Week {w}: Would create event for {iso_str}")

except Exception as e:
    import traceback
    traceback.print_exc()
