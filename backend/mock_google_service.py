from typing import List, Dict, Any
from .db import supabase

def get_mock_google_members(google_group_id: str) -> List[str]:
    """
    Returns a mock list of emails currently in a Google Group.
    Used for simulation purposes.
    """
    # Simulate some existing members in Google Groups
    # We'll use some emails that might or might not exist in Supabase
    return [
        "already_exists@gmail.com",
        "to_be_removed@gmail.com",
    ]

async def sync_to_google(group_id: str) -> Dict[str, Any]:
    """
    Simulates syncing a Supabase group to a Google Group.
    1. Fetch ground truth from Supabase.
    2. Fetch mock current state from Google.
    3. Calculate delta.
    4. Log the "actions".
    """
    try:
        # 1. Fetch group details
        group_res = supabase.table("user_groups").select("*").eq("id", group_id).execute()
        if not group_res.data:
            return {"status": "error", "message": "Group not found"}
        
        group = group_res.data[0]
        group_name = group.get("name")
        google_group_id = group.get("google_group_id") or f"mock-{group_name.lower().replace(' ', '-')}"

        # 2. Fetch Supabase members (Ground Truth)
        # We need their emails from the profiles table
        members_res = supabase.table("profile_groups")\
            .select("profiles(email)")\
            .eq("group_id", group_id)\
            .execute()
        
        supabase_emails = set()
        if members_res.data:
            for m in members_res.data:
                if m.get("profiles") and m["profiles"].get("email"):
                    supabase_emails.add(m["profiles"]["email"])

        # 3. Fetch Mock Google Members
        google_emails = set(get_mock_google_members(google_group_id))

        # 4. Calculate Delta
        to_add = list(supabase_emails - google_emails)
        to_remove = list(google_emails - supabase_emails)

        # 5. Log the simulation report
        print("\n" + "="*50)
        print(f"MOCK SYNC REPORT FOR GROUP: {group_name}")
        print(f"Google Group ID: {google_group_id}")
        print(f"Ground Truth (Supabase): {len(supabase_emails)} users")
        print(f"Current State (Mock Google): {len(google_emails)} users")
        print("-" * 50)
        print(f"ACTIONS TO BE TAKEN:")
        for email in to_add:
            print(f"  [+] ADD to Google: {email}")
        for email in to_remove:
            print(f"  [-] REMOVE from Google: {email}")
        if not to_add and not to_remove:
            print("  [=] NO CHANGES NEEDED - ALREADY IN SYNC")
        print("="*50 + "\n")

        return {
            "status": "success",
            "group_name": group_name,
            "added": to_add,
            "removed": to_remove,
            "summary": f"Mock Sync Complete: Added {len(to_add)}, Removed {len(to_remove)}"
        }
    except Exception as e:
        print(f"Error in mock sync: {e}")
        return {"status": "error", "message": str(e)}
