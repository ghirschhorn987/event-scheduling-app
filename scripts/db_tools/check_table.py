import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv("backend/.env")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(url, key)

try:
    res = supabase.table("user_groups").select("*").limit(1).execute()
    if res.data:
        print("Columns in user_groups:", res.data[0].keys())
    else:
        print("user_groups table is empty, but accessible.")
except Exception as e:
    print("FAILED:", e)
