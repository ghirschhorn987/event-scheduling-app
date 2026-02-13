import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def update_user_names():
    print("--- Updating User Names ---")
    
    page = 1
    users = []
    
    # Fetch all users
    while True:
        res = supabase.auth.admin.list_users(page=page, per_page=100)
        # Handle list structure variations
        batch = res if isinstance(res, list) else (res.users if hasattr(res, 'users') else [])
        if not batch:
            break
        users.extend(batch)
        page += 1
        
    print(f"Found {len(users)} users.")
    
    for u in users:
        email = u.email
        if not email: continue
        
        # Extract username
        username = email.split('@')[0]
        
        print(f"Processing {email} -> {username}")
        
        # 1. Update Auth Metadata
        try:
            supabase.auth.admin.update_user_by_id(
                u.id, 
                {"user_metadata": {"full_name": username}}
            )
        except Exception as e:
            print(f"  Error updating Auth metadata: {e}")
            
        # 2. Update Profile Name
        try:
            # Check if profile exists first? Upsert is safer if ID exists.
            # But we only want to update name if row exists.
            # Upsert might create a row without other needed data? 
            # Profile only has ID and Name now. So upsert is fine.
            supabase.table("profiles").upsert({
                "id": u.id,
                "name": username
            }).execute()
        except Exception as e:
            print(f"  Error updating Profile: {e}")

    print("--- Update Complete ---")

if __name__ == "__main__":
    update_user_names()
