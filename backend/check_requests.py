import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

emails = [
    "liliagh@gmail.com",
    "afeuer@google.com",
    "admin@skeddle.net",
    "dwaghalter@gmail.com",
    "bmbachrach@gmail.com",
    "geehirschh99@gmail.com"
]

res = supabase.table("registration_requests").select("email, status").in_("email", emails).execute()
for r in res.data:
    print(f"{r['email']}: {r['status']}")

# Also check if any of these were bulk imported vs requested
for email in emails:
    if email not in [r['email'] for r in res.data]:
        print(f"{email}: No registration request found (Likely bulk imported or manually added Admin)")

