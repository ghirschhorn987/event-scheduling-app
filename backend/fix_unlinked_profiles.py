"""
One-time script to fix unlinked profiles.
Finds auth.users records that have a matching profile by email but 
where the profile's auth_user_id is NULL, and links them.
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found.")
    exit(1)

supabase = create_client(url, key)

def fix_unlinked():
    print("--- Fixing Unlinked Profiles ---\n")
    
    # 1. Get all auth users
    all_auth = supabase.auth.admin.list_users()
    auth_by_email = {}
    for u in all_auth:
        email = getattr(u, 'email', None)
        if email:
            auth_by_email[email.lower()] = u
    
    # 2. Get all profiles with NULL auth_user_id
    unlinked = supabase.table("profiles").select("id, email, name, auth_user_id").is_("auth_user_id", "null").execute()
    
    if not unlinked.data:
        print("No unlinked profiles found. Everything is linked!")
        return
    
    print(f"Found {len(unlinked.data)} unlinked profiles.\n")
    
    linked_count = 0
    skipped_count = 0
    
    for profile in unlinked.data:
        email = (profile.get("email") or "").lower()
        if not email:
            skipped_count += 1
            continue
        
        if email in auth_by_email:
            auth_user = auth_by_email[email]
            app_meta = getattr(auth_user, 'app_metadata', {}) or {}
            auth_method = 'google' if 'google' in app_meta.get('providers', []) else 'email'
            
            print(f"  LINKING: {profile['email']} ({profile.get('name')})")
            print(f"    Profile ID:  {profile['id']}")
            print(f"    Auth ID:     {auth_user.id}")
            print(f"    Auth Method: {auth_method}")
            
            try:
                supabase.table("profiles").update({
                    "auth_user_id": auth_user.id,
                    "auth_method": auth_method
                }).eq("id", profile["id"]).execute()
                linked_count += 1
                print(f"    ✅ Success")
            except Exception as e:
                print(f"    ❌ Error: {e}")
        else:
            print(f"  SKIPPED: {profile['email']} ({profile.get('name')}) - No matching auth user found (user hasn't created account yet)")
            skipped_count += 1
    
    print(f"\n--- Summary ---")
    print(f"Successfully linked: {linked_count}")
    print(f"Skipped (no auth user): {skipped_count}")

if __name__ == "__main__":
    fix_unlinked()
