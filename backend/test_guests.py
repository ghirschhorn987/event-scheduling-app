print("DEBUG: Script started...")

import requests
import json
import time
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")
print("DEBUG: Env loaded...")
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
print("DEBUG: Supabase client created...")

BASE_URL = "http://localhost:8000"

def get_admin_headers():
    return {"Authorization": "Bearer mock-token-admin"}

def get_user_headers(uid="test-guest-tester"):
    return {"Authorization": f"Bearer mock-token-{uid}"}

def run_tests():
    print("Starting Guest Feature Verification...")

    # 1. Get an Event
    print("\n1. Fetching all events (admin)...")
    res = requests.get(f"{BASE_URL}/api/admin/events", headers=get_admin_headers())
    events = res.json().get("data", [])
    if not events:
        print("No events found. Please create one.")
        return
    # Find an open event
    open_events = [e for e in events if e.get("status") in ("OPEN_FOR_ROSTER", "OPEN_FOR_RESERVES")]
    if not open_events:
        print("No OPEN events found, using the first one anyway, but signup might fail.")
        event = events[0]
    else:
        event = open_events[0]
    
    event_id = event["id"]
    print(f"Using Event: {event['event_type_name']} ({event_id}) Status: {event['status']}")

    # 2. Get the correct User Group for this Event Type
    event_type_id = event["event_type_id"]
    print(f"\n2. Fetching user group for event type {event_type_id}...")
    try:
        et_res = supabase.table("event_types").select("roster_user_group").eq("id", event_type_id).single().execute()
        group_id = et_res.data["roster_user_group"]
        
        # Get Group Name
        g_res = supabase.table("user_groups").select("name").eq("id", group_id).single().execute()
        group_name = g_res.data["name"]
        print(f"Using Group: {group_name} ({group_id})")
    except Exception as e:
        print(f"Failed to find user group for this event: {e}")
        return

    # 3. Modify Guest Limit
    print(f"\n3. Setting guest limit for group {group_name} to 2...")
    res = requests.put(
        f"{BASE_URL}/api/admin/groups/{group_id}", 
        headers=get_admin_headers(),
        json={"guest_limit": 2}
    )
    if res.status_code != 200:
        print("Failed to set guest limit:", res.status_code, res.text)
        return
    print("Guest limit set successfully.")

    # 4. Get Existing Profile for Test User
    print(f"\n4. Fetching existing profile...")
    try:
        profile_res = supabase.table("profiles").select("*").limit(1).execute()
        if not profile_res.data:
            print("No profiles exist in DB.")
            return
        test_auth_uid = profile_res.data[0]["auth_user_id"]
        test_profile_id = profile_res.data[0]["id"]
        print(f"Using profile auth_user_id: {test_auth_uid}, profile_id: {test_profile_id}")
    except Exception as e:
        print(f"Failed to fetch profile: {e}")
        return

    # 5. Add User to Group
    print(f"\n5. Adding user {test_profile_id} to group {group_id}...")
    res = requests.post(
        f"{BASE_URL}/api/admin/groups/{group_id}/members/batch",
        headers=get_admin_headers(),
        json={"profile_ids": [test_profile_id]}
    )
    if res.status_code != 200:
        print("Failed to add user to group:", res.json())
        # Might already be in the group, continue anyway
    else:
        print("User added to group.")

    # 6. Try to Sign Up Main User
    print(f"\n6. Signing up main user {test_auth_uid}...")
    res = requests.post(
        f"{BASE_URL}/api/signup",
        headers=get_user_headers(test_auth_uid),
        json={"event_id": event_id, "user_id": test_auth_uid, "is_guest": False}
    )
    if res.status_code == 200:
        print("Main user signed up successfully.")
    else:
        print("Main user signup result:", res.status_code, res.text)
        # They might already be signed up, which is fine (400 User already signed up)

    # 7. Add Guest 1
    print("\n7. Adding Guest 1...")
    res1 = requests.post(
        f"{BASE_URL}/api/signup",
        headers=get_user_headers(test_auth_uid),
        json={"event_id": event_id, "user_id": test_auth_uid, "is_guest": True, "guest_name": "Bob Guest1"}
    )
    if res1.status_code == 200:
        guest1_data = res1.json()["data"]
        print("Guest 1 added successfully:", guest1_data)
        guest1_id = guest1_data["id"]

        # Verify Waitlist/Tier
        if guest1_data["list_type"] not in ("WAITLIST", "WAITLIST_HOLDING"):
            print("ERROR: Guest not placed in waitlist/holding!")
        else:
            print(f"SUCCESS: Guest is in {guest1_data['list_type']}")
        
        if guest1_data["tier"] != 0:
            print(f"ERROR: Guest tier {guest1_data['tier']} != 0")
        else:
            print("SUCCESS: Guest tier is 0")
    else:
        print("Failed to add Guest 1:", res1.status_code, res1.text)
        return

    # 8. Add Guest 2
    print("\n8. Adding Guest 2...")
    res2 = requests.post(
        f"{BASE_URL}/api/signup",
        headers=get_user_headers(test_auth_uid),
        json={"event_id": event_id, "user_id": test_auth_uid, "is_guest": True, "guest_name": "Alice Guest2"}
    )
    if res2.status_code == 200:
        print("Guest 2 added successfully.")
    else:
        print("Failed to add Guest 2:", res2.status_code, res2.text)

    # 9. Try adding Guest 3 (Should fail limit)
    print("\n9. Adding Guest 3 (should fail due to limit = 2)...")
    res3 = requests.post(
        f"{BASE_URL}/api/signup",
        headers=get_user_headers(test_auth_uid),
        json={"event_id": event_id, "user_id": test_auth_uid, "is_guest": True, "guest_name": "Charlie Guest3"}
    )
    if res3.status_code == 400:
        print("SUCCESS: Guest 3 correctly blocked:", res3.text)
    else:
        print("ERROR: Expected HTTP 400, got:", res3.status_code, res3.text)

    # 10. Remove Guest 1
    print("\n10. Removing Guest 1...")
    rm_res = requests.post(
        f"{BASE_URL}/api/remove-signup",
        headers=get_user_headers(test_auth_uid),
        json={"event_id": event_id, "user_id": test_auth_uid, "signup_id": guest1_id}
    )
    if rm_res.status_code == 200:
        print("Guest 1 removed successfully.")
    else:
        print("Failed to remove Guest 1:", rm_res.status_code, rm_res.text)

    # Wait, if guest is removed, can we add a new one?
    print("\n11. Trying Guest 3 again (should succeed since we have a free slot)...")
    res_retry = requests.post(
        f"{BASE_URL}/api/signup",
        headers=get_user_headers(test_auth_uid),
        json={"event_id": event_id, "user_id": test_auth_uid, "is_guest": True, "guest_name": "Charlie Guest3"}
    )
    if res_retry.status_code == 200:
        print("SUCCESS: Guest 3 added successfully. Guest slot freed correctly.")
    else:
        print("ERROR: Failed to add Guest 3:", res_retry.status_code, res_retry.text)

    print("\nVerification Complete.")


if __name__ == '__main__':
    run_tests()
