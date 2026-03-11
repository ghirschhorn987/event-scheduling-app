import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

# Check if the trigger exists
res = supabase.rpc('', {})
# Actually, let's try via raw SQL
# Check if the trigger function exists
query = """
SELECT routine_name, routine_definition 
FROM information_schema.routines 
WHERE routine_name = 'handle_new_user' AND routine_schema = 'public'
"""
# Supabase doesn't allow raw SQL via client, so let's just check if 
# we can call the function or check triggers differently

# Check for all 5 orphaned auth users - maybe they ALL signed up via Google?
all_auth = supabase.auth.admin.list_users()
orphan_auth_ids = [
    "4ba5ab39-49fe-4081-80b8-2cc54a1fc94d",  # ghirschhorn@skeddle.net
    "d6d2ba30-ce82-45e5-87d4-83a33db834d0",  # afeuer@google.com
    "afc367c2-a34e-4339-ac37-9750ae5dc09e",  # dwaghalter@gmail.com
    "dd6fab6e-fc5b-4753-9ce4-a23dd1e46f89",  # ghirschhorn@google.com
    "d5115d40-7b61-44f4-8bcc-7fc263404efb",  # test2@skeddle.com
]

print("=== Auth users MISSING a profile ===")
for u in all_auth:
    if u.id in orphan_auth_ids:
        app_meta = getattr(u, 'app_metadata', {}) or {}
        print(f"  {u.email}: provider={app_meta.get('provider', 'unknown')}, providers={app_meta.get('providers', [])}, created={u.created_at}")

# Now check the 6 profiles missing auth - what's their auth_user_id?
print("\n=== Profiles MISSING an auth record ===")
orphan_profile_emails = [
    "liliagh@gmail.com",
    "afeuer@google.com",
    "admin@skeddle.net",
    "dwaghalter@gmail.com",
    "bmbachrach@gmail.com",
    "geehirschh99@gmail.com"
]

for email in orphan_profile_emails:
    res = supabase.table("profiles").select("id, email, name, auth_user_id").eq("email", email).execute()
    if res.data:
        p = res.data[0]
        print(f"  {p['email']} ({p.get('name')}): auth_user_id={p.get('auth_user_id')}")
