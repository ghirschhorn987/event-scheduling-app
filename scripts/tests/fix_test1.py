import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("backend/.env")
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def fix_test1():
    email = "test1@skeddle.club"
    password = "test1test1"
    name = "Test Admin"
    
    print(f"Fixing {email}...")
    
    # 1. Find Auth User
    user_id = None
    try:
        page = 1
        found = False
        while True:
            res = supabase.auth.admin.list_users(page=page, per_page=50)
            users = res if isinstance(res, list) else (res.users if hasattr(res, 'users') else [])
            if not users:
                break
            
            print(f"  Page {page}: Found {len(users)} users")
            for u in users:
                if u.email == email:
                    user_id = u.id
                    print(f"  Found via list_users: {user_id}")
                    found = True
                    break
            if found:
                break
            page += 1
            if page > 10: break # Safety
    except Exception as e:
        print(f"  list_users failed: {e}")

    if not user_id:
        print("  Trying sign_in to find user...")
        try:
            session = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if session and session.user:
                user_id = session.user.id
                print(f"  Found via sign_in: {user_id}")
        except Exception as e:
            print(f"  sign_in failed: {e}")
            # Try with old password "test1"?
            try:
                session = supabase.auth.sign_in_with_password({"email": email, "password": "test1"})
                if session and session.user:
                    user_id = session.user.id
                    print(f"  Found via sign_in (old pass): {user_id}")
            except:
                pass
            
    # 2. Delete if exists (to ensure clean slate with profile)
    if user_id:
        print("  Deleting existing user...")
        supabase.auth.admin.delete_user(user_id)
        
    # 3. Create fresh
    print("  Creating user...")
    try:
        user = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"full_name": name}
        })
        user_id = user.user.id
        print(f"  Created user: {user_id}")
    except Exception as e:
        print(f"  Failed to create user: {e}")
        return

    # 4. Profile
    print("  Creating profile...")
    supabase.table("profiles").insert({"id": user_id, "name": name}).execute()
    
    # 5. Group
    print("  Assigning to Admin group...")
    g_res = supabase.table("user_groups").select("id").eq("name", "Admin").single().execute()
    if g_res.data:
        g_id = g_res.data['id']
        supabase.table("profile_groups").insert({"profile_id": user_id, "group_id": g_id}).execute()
        print("  Assigned.")
        
    # 6. Update JSON
    new_user = {
        "id": user_id,
        "email": email,
        "name": name,
        "groups": ["Admin"]
    }
    
    try:
        with open("frontend/src/mock_users.json", "r") as f:
            data = json.load(f)
        data.append(new_user)
        with open("frontend/src/mock_users.json", "w") as f:
            json.dump(data, f, indent=2)
        print("  Updated mock_users.json")
    except Exception as e:
        print(f"  Failed to update JSON: {e}")

if __name__ == "__main__":
    fix_test1()
