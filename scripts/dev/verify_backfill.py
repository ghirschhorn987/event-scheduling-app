import os
import sys
import requests
import time
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path to import backend modules if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

# Load env from backend/.env
# Note: we should load from backend/.env explicitly
env_path = os.path.join(os.path.dirname(__file__), '../../backend/.env')
load_dotenv(env_path)

API_URL = "http://localhost:8000/api"
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing SUPABASE_URL or SUPABASE_KEY in env")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_signup(event_id, user_id):
    # user_id here is the AUTH ID (from mock token)
    # Get profile ID
    res = supabase.table("profiles").select("id").eq("auth_user_id", user_id).execute()
    if not res.data:
        return None
    profile_id = res.data[0]['id']
    
    res = supabase.table("event_signups").select("*").eq("event_id", event_id).eq("user_id", profile_id).execute()
    return res.data[0] if res.data else None

def get_all_signups(event_id):
    res = supabase.table("event_signups").select("*").eq("event_id", event_id).order("list_type").order("sequence_number").execute()
    return res.data

def verify_backfill():
    print("Starting Backfill Verification...")
    
    # 1. Setup: Fetch Event
    try:
        res = requests.get(f"{API_URL}/events", headers={"Authorization": "Bearer mock-token-user1"})
        if res.status_code != 200:
             print(f"Failed to fetch events: {res.status_code} {res.text}")
             return
             
        events = res.json()
        if not events:
            print("No events found. Please seed data or create an event.")
            return
        
        target_event = events[0]
        event_id = target_event['id']
        # We need the roster group ID to add users to it
        # Events endpoint returns enrolled counts but maybe not the group ID directly in top level? 
        # API response structure: "roster_user_group": {id, name} (from logic.py enrich_event?)
        # Let's check logic.py: event_data["roster_user_group"] = event_type.get("roster_user_group")
        # And models.py/schema?
        # The API response usually includes it if enriched.
        
        roster_group_id = None
        if target_event.get('roster_user_group'):
            # It might be an object or ID depending on API. logic.py puts the object/dict if available from join?
            # main.py list_events -> enriched_events.
            # verify response structure or just query DB.
            # Let's query DB for certainty.
            evt_res = supabase.table("events").select("event_types(roster_user_group)").eq("id", event_id).single().execute()
            if evt_res.data and evt_res.data.get('event_types'):
                 roster_group_id = evt_res.data['event_types']['roster_user_group']
        
        if not roster_group_id:
             print("Could not find roster_user_group for event. Cannot verify eligibility.")
             return

        print(f"Using Event: {target_event['name']} ({event_id}) max={target_event.get('max_signups', '?')}")
        print(f"Roster Group: {roster_group_id}")
        
    except Exception as e:
        print(f"Failed to fetch events: {e}")
        return

    # 2. Cleanup & Seed
    # Use real existing auth_user_ids to satisfy FK constraints
    users = [
        "98ef110a-e89d-4fc9-8429-0f1edf5b4bf0",
        "d65b7bf9-b147-468b-a420-bd7a7b61f809",
        "bab0de9a-c8c1-4065-80d5-c73d1dc23a74",
        "73fe7ef8-8e74-4f53-8c89-4697094e01db",
        "4f8ae5f3-f547-430d-8a73-365cd40624ba"
    ]
    print("\n--- Cleaning up previous signups & Seeding Users ---")
    
    # Delete ALL signups for this event to be clean
    supabase.table("event_signups").delete().eq("event_id", event_id).execute()
    
    for i, u in enumerate(users):
        # 1. Upsert Profile
        # We need a stable ID for the profile too, or let DB gen it.
        # Let's use the AUTH ID as the Profile ID for simplicity if allowed?
        # Schema might allow. The app uses auth_user_id link.
        # Let's just lookup or insert.
        
        # Check if profile exists
        p_res = supabase.table("profiles").select("id").eq("auth_user_id", u).execute()
        profile_id = None
        if p_res.data and len(p_res.data) > 0:
            profile_id = p_res.data[0]['id']
        else:
            # Create
            new_p = {
                "auth_user_id": u,
                "email": f"mock{i}@test.com",
                "name": f"Mock User {i}"
            }
            c_res = supabase.table("profiles").insert(new_p).execute()
            profile_id = c_res.data[0]['id']
            
        # 2. Add to Roster Group
        # Check if in group
        pg_res = supabase.table("profile_groups").select("*").eq("profile_id", profile_id).eq("group_id", roster_group_id).execute()
        if not pg_res.data:
            supabase.table("profile_groups").insert({
                "profile_id": profile_id,
                "group_id": roster_group_id
            }).execute()

    # 3. Populate
    print("\n--- Populating Users ---")
    signups = []
    for u in users:
        res = requests.post(f"{API_URL}/signup", 
                           json={"event_id": event_id, "user_id": u},
                           headers={"Authorization": f"Bearer mock-token-{u}"})
        
        if res.status_code != 200:
            print(f"User {u} signup failed: {res.text}")
        else:
            data = res.json()['data']
            print(f"User {u} signed up: {data['list_type']} #{data['sequence_number']}")
            signups.append(data)

    # Check state
    current_signups = get_all_signups(event_id)
    print(f"Current State ({len(current_signups)} users)")

    if len(current_signups) < 3:
        print("Skipping test due to insufficient signups.")
        return

    # 4. Remove Middle user
    # Identify victim. Let's pick the one at index 1 (2nd user).
    # Since we wiped DB, current_signups should match our users list order (mostly).
    victim_signup = current_signups[1]
    
    # Find auth ID for this signup
    # We can just map back via profile_id -> auth_id
    p_res = supabase.table("profiles").select("auth_user_id").eq("id", victim_signup['user_id']).single().execute()
    victim_auth = p_res.data['auth_user_id']
    
    print(f"\n--- Removing User {victim_auth} (Seq {victim_signup['sequence_number']}) ---")
    res = requests.post(f"{API_URL}/remove-signup", 
                       json={"event_id": event_id, "user_id": victim_auth},
                       headers={"Authorization": f"Bearer mock-token-{victim_auth}"})

    print(f"Response: {res.status_code}")

    # 5. Verify
    new_signups = get_all_signups(event_id)
    print("New State:")
    for s in new_signups:
        print(f" - User {s['user_id']} : {s['list_type']} #{s['sequence_number']}")
        
    # Validation
    # Check sequences PER LIST
    by_list = {}
    for s in new_signups:
        l = s['list_type']
        if l not in by_list: by_list[l] = []
        by_list[l].append(s['sequence_number'])
        
    all_passed = True
    for ltype, seqs in by_list.items():
        seqs.sort()
        expected = list(range(1, len(seqs) + 1))
        if seqs != expected:
            print(f"❌ FAILED: Gaps in {ltype} sequence! Got {seqs}, expected {expected}")
            all_passed = False
        else:
            print(f"✅ PASSED: {ltype} sequence is contiguous.")
            
    if all_passed:
        # Check promotion if applicable
        # If we had overflow (Waitlist) and removed from Event, did someone promote?
        # We need to know max_signups.
        max_s = target_event.get('max_signups', 100)
        
        event_count = len(by_list.get('EVENT', []))
        wl_count = len(by_list.get('WAITLIST', []))
        
        if event_count < max_s and wl_count > 0:
             print(f"❌ FAILED: Event has space ({event_count} < {max_s}) but Waitlist has {wl_count} users!")
        elif event_count == max_s and wl_count > 0:
             print("✅ PASSED: Event is full, Waitlist preserved.")
        elif wl_count == 0:
             print("✅ PASSED: Waitlist empty (everyone likely promoted).")

if __name__ == "__main__":
    verify_backfill()
