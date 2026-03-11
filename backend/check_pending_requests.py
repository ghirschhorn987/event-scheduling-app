import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

# 1. Fetch all registration requests
requests_res = supabase.table("registration_requests").select("id, email, status").execute()
requests = requests_res.data
pending_requests = [r for r in requests if r['status'] == 'PENDING']

# 2. Fetch all profiles
profiles_res = supabase.table("profiles").select("email").execute()
profile_emails = {p['email'].lower() for p in profiles_res.data if p.get('email')}

print(f"Total Registration Requests: {len(requests)}")
print(f"Pending Requests: {len(pending_requests)}")

print("\n--- Details of Pending Requests ---")
for req in pending_requests:
    email = req['email'].lower()
    has_profile = email in profile_emails
    print(f"[{'X' if has_profile else ' '}] {req['email']} (Has Profile: {has_profile})")

