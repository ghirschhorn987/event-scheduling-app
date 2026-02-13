import os
import sys
from datetime import datetime, timezone

# Add parent directory to path to import modules
# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db import supabase
from logic import enrich_event, determine_event_status

def get_now():
    return datetime.now(timezone.utc)

def migrate():
    print("Starting Event Status Migration...")
    
    # Fetch all events (including finished/cancelled to be safe, though maybe we leave them? 
    # User said "Delete all statuses other than the 7 new ones". So we better double check everything.)
    # Actually, we should respect "CANCELLED" if it's already there?
    # User said: "For CANCELLED status, please change all use to "Cancelled" instead."
    # Wait, my Enum has "CANCELLED" (all caps). I should stick to my Enum.
    
    try:
        events_res = supabase.table("events").select("*, event_types(*)").execute()
        
        if not events_res.data:
            print("No events found.")
            return

        enriched_events = [enrich_event(e) for e in events_res.data]
        now = get_now()
        
        count = 0
        for event in enriched_events:
            current_status = event.get("status")
            
            # Special handling for explicit "CANCELLED" or legacy "Cancelled"
            if current_status in ["CANCELLED", "Cancelled", "cancelled"]:
                # Ensure it is the canonical CANCELLED
                if current_status != "CANCELLED":
                    print(f"Fixing Cancelled case for {event['id']}")
                    supabase.table("events").update({"status": "CANCELLED"}).eq("id", event["id"]).execute()
                continue

            # Derived Status
            new_status = determine_event_status(event, now)
            
            if new_status != current_status:
                print(f"Migrating Event {event['name']} ({event['event_date']}): {current_status} -> {new_status}")
                supabase.table("events").update({"status": new_status}).eq("id", event["id"]).execute()
                count += 1
                
        print(f"Migration Complete. Updated {count} events.")
    
    except Exception as e:
        err_msg = str(e)
        if "invalid input value for enum" in err_msg:
             print("\n❌ CRITICAL ERROR: The database Enum definitions are out of date.")
             print("Please run the SQL migration script from the Supabase Dashboard:")
             print("See: database/migrations/safe_add_enum.sql")
        else:
             print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    migrate()
