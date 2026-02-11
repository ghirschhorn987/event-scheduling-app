import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def recreate_test1():
    email = "test1@skeddle.club"
    password = "test1test1"
    name = "test1"  # Matching email username per request
    
    print(f"--- Re-creating {email} ---")
    
    # 1. Double check deletion (optional, but good)
    # If user truly deleted manuall, list_users should not find it.
    
    # 2. Create User
    print("  Creating auth user...")
    try:
        res = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"full_name": name}
        })
        user_id = res.user.id
        print(f"  Created user ID: {user_id}")
    except Exception as e:
        print(f"  Error creating user: {e}")
        return

    # 3. Create Profile
    print("  Creating profile...")
    try:
        supabase.table("profiles").insert({
            "id": user_id,
            "name": name
        }).execute()
    except Exception as e:
        print(f"  Error creating profile: {e}")

    # 4. Assign Admin Group
    print("  Assigning Admin group...")
    try:
        # Get Group ID
        g_res = supabase.table("user_groups").select("id").eq("name", "Admin").single().execute()
        if g_res.data:
            gid = g_res.data['id']
            supabase.table("profile_groups").insert({
                "profile_id": user_id,
                "group_id": gid
            }).execute()
            print("  Assigned to Admin group.")
        else:
            print("  Could not find 'Admin' group!")
    except Exception as e:
        print(f"  Error assigning group: {e}")

    print("--- Done ---")

if __name__ == "__main__":
    recreate_test1()
