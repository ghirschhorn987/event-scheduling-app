
import sys
import os
from datetime import datetime, timezone
from pprint import pprint

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

try:
    from db import supabase
    from logic import enrich_event, determine_event_status
except Exception as e:
    print(f"Error importing backend modules: {e}")
    sys.exit(1)

EVENT_ID = "94c035fa-d37e-4603-ada2-75d2a92a4e60"

def check_status():
    print(f"Checking status for event: {EVENT_ID}")
    
    # 1. Fetch Event
    try:
        response = supabase.table("events").select("*, event_types(*)").eq("id", EVENT_ID).single().execute()
        if not response.data:
            print("Event not found in DB.")
            return
        
        raw_event = response.data
        print(f"DB Status: {raw_event.get('status')}")
        print(f"Event Date: {raw_event.get('event_date')}")
        
    except Exception as e:
        print(f"Error fetching event: {e}")
        return

    # 2. Enrich
    now = datetime.now(timezone.utc)
    print(f"Current Time (UTC): {now}")
    
    enriched = enrich_event(raw_event, now)
    
    print("\n--- Calculated Timestamps ---")
    print(f"Roster Open: {enriched.get('roster_sign_up_open')}")
    print(f"Reserve Open: {enriched.get('reserve_sign_up_open')}")
    print(f"Initial Scheduling: {enriched.get('initial_reserve_scheduling')}")
    print(f"Final Scheduling: {enriched.get('final_reserve_scheduling')}")
    
    # 3. Determine Status
    calculated_status = determine_event_status(enriched, now)
    print(f"\nCalculated Status: {calculated_status}")
    
    if calculated_status != raw_event.get('status'):
        print(f"\nMISMATCH! DB says {raw_event.get('status')}, Logic says {calculated_status}")
    else:
        print("\nMatch. The status is correct according to logic.")

if __name__ == "__main__":
    check_status()
