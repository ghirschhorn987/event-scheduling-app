
import os
import sys
from dotenv import load_dotenv

# Path to backend .env
dotenv_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(dotenv_path)

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from db import supabase
    print("✅ Successfully imported Supabase client.")
except Exception as e:
    print(f"❌ Failed to import Supabase client: {e}")
    sys.exit(1)

def check_admin_groups():
    print("\n--- Checking User Groups ---")
    try:
        res = supabase.table("user_groups").select("*").execute()
        print(f"Found {len(res.data)} groups:")
        for g in res.data:
            print(f"  - {g['name']} (ID: {g['id']})")
    except Exception as e:
        print(f"Error fetching groups: {e}")

    print("\n--- Checking Admin Users ---")
    try:
        # Check profiles with Admin/Super Admin/SuperAdmin groups
        res = supabase.table("profiles").select("name, email, profile_groups(user_groups(name))").execute()
        
        found_admin = False
        for p in res.data:
            groups = []
            if p.get("profile_groups"):
                for pg in p["profile_groups"]:
                    if pg.get("user_groups"):
                        groups.append(pg["user_groups"]["name"])
            
            if any(g in ["Admin", "Super Admin", "SuperAdmin"] for g in groups):
                print(f"Admin Found: {p['name']} ({p.get('email', 'N/A')}) -> Groups: {groups}")
                found_admin = True
        
        if not found_admin:
            print("No users found with Admin/Super Admin privileges.")

    except Exception as e:
        print(f"Error checking admins: {e}")

if __name__ == "__main__":
    check_admin_groups()
