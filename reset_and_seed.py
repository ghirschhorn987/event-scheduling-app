import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in backend/.env")

supabase: Client = create_client(url, key)

def run_sql_migration():
    """
    Attempts to execute the migration SQL.
    Since we don't have direct SQL access via python client easily without extensions,
    we will rely on the user running it or a workaround if available.
    """
    print("\n--- Checking Schema ---")
    try:
        # Check if profile_groups table exists by selecting from it
        supabase.table("profile_groups").select("count", count="exact").limit(1).execute()
        print("✅ profile_groups table exists.")
    except Exception as e:
        print("❌ profile_groups table NOT FOUND or accessible.")
        print("Please execute the following SQL in your Supabase SQL Editor:")
        print("-" * 40)
        with open("backend/database/migrations/refactor_user_management.sql", "r") as f:
            print(f.read())
        print("-" * 40)
        input("Press Enter after you have run the modification SQL...")

def reset_data():
    print("\n--- Resetting Data ---")
    
    # 1. Truncate Tables
    # We can't use TRUNCATE via PostgREST unless exposed as RPC.
    # We have to delete all rows.
    # Deleting users is hard because of FK constraints if we don't cascade,
    # but `auth.users` deletion cascades to `profiles` usually if configured (ON DELETE CASCADE).
    # Our `profiles` table references `auth.users`.
    
    # Actually, the user asked to "delete all existing rows from users and profiles table".
    # `auth.users` is harder to clear via API. We have `supabase.auth.admin.list_users()` and `delete_user()`.
    
    print("Deleting all Auth Users...")
    users = []
    page = 1
    while True:
        # returns list of User objects directly in some versions?
        # Or returns a UserList object?
        # The error said 'list' object has no attribute 'users'.
        # So res IS a list.
        res = supabase.auth.admin.list_users(page=page, per_page=100)
        if not res:
            break
        users.extend(res)
        page += 1
        
    for u in users:
        print(f"  Deleting user {u.email}...")
        try:
            supabase.auth.admin.delete_user(u.id)
        except Exception as e:
            print(f"  Error deleting user {u.email}: {e}")

    # Also clear user_groups?
    print("Clearing user_groups...")
    # This might fail if constraints exist, but we deleted users/profiles first so it should be fine.
    # RLS might block if not service role, but we use service role.
    try:
        # Fetch IDs first to delete
        res = supabase.table("user_groups").select("id").execute()
        if res.data:
            ids = [r['id'] for r in res.data]
            supabase.table("user_groups").delete().in_("id", ids).execute()
    except Exception as e:
        print(f"Error clearing user_groups: {e}")

def create_groups():
    print("\n--- Creating Groups ---")
    group_names = ["Super Admin", "Admin", "Primary", "Secondary"]
    groups = {}
    
    for name in group_names:
        # Check if exists (upsert logic basically)
        existing = supabase.table("user_groups").select("*").eq("name", name).execute()
        if existing.data:
            groups[name] = existing.data[0]['id']
            print(f"  Group '{name}' exists: {groups[name]}")
        else:
            res = supabase.table("user_groups").insert({"name": name}).execute()
            if res.data:
                groups[name] = res.data[0]['id']
                print(f"  Created Group '{name}': {groups[name]}")
                
    return groups

def create_user_with_groups(email, password, name, group_names, all_groups_map):
    print(f"Creating User: {email} ({name}) -> {group_names}")
    
    # 1. Auth User
    user_id = None
    try:
        user = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"full_name": name}
        })
        user_id = user.user.id
    except Exception as e:
        print(f"  Error creating auth user: {e}")
        # Try finding existing if error? But we just wiped data.
        return

    # 2. Profile
    try:
        supabase.table("profiles").insert({
            "id": user_id,
            "name": name
            # "email": email # Removed 
        }).execute()
    except Exception as e:
        print(f"  Error creating profile: {e}")
        return

    # 3. Assign Groups
    for g_name in group_names:
        g_id = all_groups_map.get(g_name)
        if g_id:
            try:
                supabase.table("profile_groups").insert({
                    "profile_id": user_id,
                    "group_id": g_id
                }).execute()
                print(f"  -> Assigned to {g_name}")
            except Exception as e:
                print(f"  Error assigning group {g_name}: {e}")

    return {"id": user_id, "email": email, "name": name, "groups": group_names}


def seed_data(groups_map):
    print("\n--- Seeding Users ---")
    mock_users = []

    # 1. Mock Super Admin
    u = create_user_with_groups("mock.super@test.com", "password123", "Mock Super Admin", ["Super Admin"], groups_map)
    if u: mock_users.append(u)

    # 2. 5 Mock Regular Users (Primary)
    for i in range(1, 6):
        u = create_user_with_groups(f"mock.user.{i}@test.com", "password123", f"Mock User {i}", ["Primary"], groups_map)
        if u: mock_users.append(u)

    # 3. Specific Users
    # admin@skeddle.club -> Super Admin
    u = create_user_with_groups("admin@skeddle.club", "adminadmin", "Real Admin", ["Super Admin"], groups_map)
    if u: mock_users.append(u)

    # test1@skeddle.club -> Admin
    u = create_user_with_groups("test1@skeddle.club", "test1test1", "Test Admin", ["Admin"], groups_map)
    if u: mock_users.append(u)

    # test2@skeddle.club -> Primary + Secondary
    u = create_user_with_groups("test2@skeddle.club", "test2test2", "Test User Multi", ["Primary", "Secondary"], groups_map)
    if u: mock_users.append(u)

    # Save to JSON for frontend toolbar
    import json
    with open("frontend/src/mock_users.json", "w") as f:
        json.dump(mock_users, f, indent=2)
    print(f"\nSaved {len(mock_users)} users to frontend/src/mock_users.json")

if __name__ == "__main__":
    run_sql_migration()
    # Confirmation before wipe
    # val = input("This will WIPE all user data. Type 'yes' to proceed: ")
    # if val != 'yes': exit()
    # Note: Automation script, skipping input for now but be careful.
    
    reset_data()
    groups_map = create_groups()
    seed_data(groups_map)
