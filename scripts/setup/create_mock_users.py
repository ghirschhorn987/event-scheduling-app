import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)

def create_or_get_group(name):
    print(f"Checking Group: {name}")
    res = supabase.table("user_groups").select("*").eq("name", name).execute()
    if res.data:
        return res.data[0]['id']
    
    print(f"Creating Group: {name}")
    res = supabase.table("user_groups").insert({"name": name}).execute()
    return res.data[0]['id']

def create_mock_user(email, password, name, group_id=None):
    print(f"Processing User: {email}")
    
    # 1. Check if Auth User exists (we can't easily search auth.users via client usually, 
    # but we can try to sign in or just create and catch error)
    # Actually, verify if admin api is available
    user_id = None
    
    try:
        # Try creating
        # Note: python supabase client auth.admin.create_user might vary by version
        # If this fails, we might have to use requests/GoTrue directly or just sign_up
        # But sign_up requires email confirmation usually. Admin create auto-confirms.
        
        attributes = {
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"full_name": name}
        }
        user = supabase.auth.admin.create_user(attributes)
        user_id = user.user.id
        print(f"  -> Created Auth User: {user_id}")
    except Exception as e:
        # If already exists, we need to find the ID. 
        # A simple way for a script: Try to signIn with password!
        print(f"  -> User creation failed (likely exists): {str(e)}")
        try:
            session = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user_id = session.user.id
            print(f"  -> Found Existing Auth User: {user_id}")
        except Exception as sign_in_e:
            print(f"  -> Could not login either! {sign_in_e}")
            return None

    if not user_id:
        return None

    # 2. Create/Update Profile
    profile_data = {
        "id": user_id,
        "email": email,
        "name": name,
        "user_group_id": group_id
    }
    
    # Upsert profile
    try:
        supabase.table("profiles").upsert(profile_data).execute()
        print("  -> Profile Synced")
    except Exception as e:
        print(f"  -> Profile Update Failed: {e}")

    return {"id": user_id, "email": email, "name": name, "role": "member" if group_id else "guest"}

def run():
    print("--- 1. Setup Groups ---")
    primary_group_id = create_or_get_group("Primary")
    secondary_group_id = create_or_get_group("Secondary")
    
    mock_users = []

    print("\n--- 2. Create Users ---")
    
    # Admin
    # (For now treating admin as just a user, maybe separate role logic later)
    u = create_mock_user("mock.admin@test.com", "password123", "Mock Admin", primary_group_id)
    if u: 
        u['role'] = 'admin'
        mock_users.append(u)

    # Primaries (15)
    for i in range(1, 16):
        u = create_mock_user(f"mock.primary.{i}@test.com", "password123", f"Primary {i}", primary_group_id)
        if u: 
            u['role'] = 'primary'
            mock_users.append(u)
            
    # Secondaries (10)
    for i in range(1, 11):
        u = create_mock_user(f"mock.secondary.{i}@test.com", "password123", f"Secondary {i}", secondary_group_id)
        if u: 
            u['role'] = 'secondary'
            mock_users.append(u)

    # Guests (5)
    for i in range(1, 6):
        u = create_mock_user(f"mock.guest.{i}@test.com", "password123", f"Guest {i}", None)
        if u: 
            u['role'] = 'guest'
            mock_users.append(u)

    # Save to file
    outfile = "frontend/src/mock_users.json"
    with open(outfile, "w") as f:
        json.dump(mock_users, f, indent=2)
    
    print(f"\n--- Done! Saved {len(mock_users)} users to {outfile} ---")

if __name__ == "__main__":
    run()
