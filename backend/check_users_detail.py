import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

emails = ["afeuer@google.com", "dwaghalter@gmail.com"]

# Get all auth users once
all_auth = supabase.auth.admin.list_users()

for email in emails:
    print(f"\n{'='*50}")
    print(f"  {email}")
    print(f"{'='*50}")
    
    # Profile info
    profile_res = supabase.table("profiles").select("id, email, name, auth_user_id, auth_method").eq("email", email).execute()
    if profile_res.data:
        for p in profile_res.data:
            print(f"  PROFILE:")
            print(f"    Profile ID:    {p['id']}")
            print(f"    Name:          {p.get('name')}")
            print(f"    auth_user_id:  {p.get('auth_user_id')}")
            print(f"    auth_method:   {p.get('auth_method')}")
    else:
        print("  PROFILE: None found")

    # Auth user info
    for u in all_auth:
        if hasattr(u, 'email') and u.email and u.email.lower() == email.lower():
            app_meta = getattr(u, 'app_metadata', {}) or {}
            print(f"  AUTH USER:")
            print(f"    Auth ID:       {u.id}")
            print(f"    Email:         {u.email}")
            print(f"    Provider:      {app_meta.get('provider', 'unknown')}")
            print(f"    Providers:     {app_meta.get('providers', [])}")
            print(f"    Created at:    {u.created_at}")
            print(f"    Confirmed at:  {getattr(u, 'confirmed_at', 'N/A')}")
            print(f"    Last sign in:  {getattr(u, 'last_sign_in_at', 'N/A')}")
