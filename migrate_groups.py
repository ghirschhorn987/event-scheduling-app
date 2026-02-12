
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    exit(1)

supabase: Client = create_client(url, key)
print("✅ Successfully imported Supabase client.\n")

def migrate_groups():
    # 1. Ensure Standard Groups Exist
    print("--- 1. Ensuring Standard Groups Exist ---")
    standards = [
        ("FirstPriority", "Standardized First Priority Group"),
        ("SecondPriority", "Standardized Second Priority Group")
    ]
    
    std_ids = {}
    
    for name, desc in standards:
        # Check if exists
        res = supabase.table("user_groups").select("id").eq("name", name).execute()
        if res.data:
            print(f"Group '{name}' exists.")
            std_ids[name] = res.data[0]["id"]
        else:
            print(f"Creating group '{name}'...")
            res = supabase.table("user_groups").insert({"name": name, "description": desc}).execute()
            std_ids[name] = res.data[0]["id"]

    first_id = std_ids["FirstPriority"]
    second_id = std_ids["SecondPriority"]

    # 2. Migration Logic Helper
    def migrate_group(old_name, new_id, new_name):
        print(f"\n--- Migrating '{old_name}' -> '{new_name}' ---")
        
        # Get Old ID
        res = supabase.table("user_groups").select("id").eq("name", old_name).execute()
        if not res.data:
            print(f"Old group '{old_name}' not found. Skipping.")
            return

        old_id = res.data[0]["id"]
        if old_id == new_id:
            print("Old ID matches New ID. Nothing to do.")
            return

        print(f"Found '{old_name}' ({old_id}). Moving users...")

        # Move Users (profile_groups)
        # Fetch all members of old group
        pg_res = supabase.table("profile_groups").select("profile_id").eq("group_id", old_id).execute()
        members = [r["profile_id"] for r in pg_res.data]
        
        if members:
            print(f"Found {len(members)} members in old group.")
            # Insert into new group
            inserts = [{"profile_id": pid, "group_id": new_id} for pid in members]
            try:
                supabase.table("profile_groups").insert(inserts).execute()
                print(f"Added {len(members)} members to '{new_name}'.")
            except Exception as e:
                # Likely constraint violation if they are already in the new group
                if "duplicate" in str(e) or "unique" in str(e):
                     print("Some members were already in the new group (Duplicate ignored).")
                else:
                    print(f"Error moving members: {e}")

            # Delete from old group
            supabase.table("profile_groups").delete().eq("group_id", old_id).execute()
            print("Removed members from old group.")
        else:
             print("No members to move.")

        # Update Event Types that reference old group
        # Check types referencing old_id as FIRST priority
        et_res1 = supabase.table("event_types").select("*").eq("reserve_first_priority_user_group", old_id).execute()
        for et in et_res1.data:
            print(f"Updating Event Type '{et['name']}' (First Priority)...")
            supabase.table("event_types").update({"reserve_first_priority_user_group": new_id}).eq("id", et["id"]).execute()

        # Check types referencing old_id as SECOND priority
        et_res2 = supabase.table("event_types").select("*").eq("reserve_second_priority_user_group", old_id).execute()
        for et in et_res2.data:
            print(f"Updating Event Type '{et['name']}' (Second Priority)...")
            supabase.table("event_types").update({"reserve_second_priority_user_group": new_id}).eq("id", et["id"]).execute()

        # Delete Old Group
        print(f"Deleting old group '{old_name}'...")
        supabase.table("user_groups").delete().eq("id", old_id).execute()
        print("Done.")

    # 3. Execute Migrations
    migrate_group("SecondaryPriority", second_id, "SecondPriority")
    migrate_group("Secondary", second_id, "SecondPriority")
    migrate_group("Primary", first_id, "FirstPriority")
    
    # 4. Explicitly Fix Event Types (to ensure they point to new IDs)
    print("\n--- 4. Enforcing Event Type Links ---")
    # All event types should now point to First/Second Priority IDs
    
    # Update all to FirstPriority
    supabase.table("event_types").update({"reserve_first_priority_user_group": first_id}).neq("reserve_first_priority_user_group", first_id).execute()
    
    # Update all to SecondPriority
    supabase.table("event_types").update({"reserve_second_priority_user_group": second_id}).neq("reserve_second_priority_user_group", second_id).execute()
    
    print("Event Types updated.")

if __name__ == "__main__":
    migrate_groups()
