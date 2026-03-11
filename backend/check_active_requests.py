import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

requests_res = supabase.table("registration_requests").select("id, email, status").execute()
requests = requests_res.data
active_requests = [r for r in requests if r['status'] in ['PENDING', 'INFO_NEEDED']]

profiles_res = supabase.table("profiles").select("email").execute()
profile_emails = {p['email'].lower() for p in profiles_res.data if p.get('email')}

print(f"Active Requests (PENDING or INFO_NEEDED): {len(active_requests)}")
print("\n--- Details ---")
for req in active_requests:
    email = req['email'].lower()
    has_profile = email in profile_emails
    print(f"[{req['status']}] {req['email']} (Has Profile: {has_profile})")
