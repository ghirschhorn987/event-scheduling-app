import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv("backend/.env")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(url, key)

try:
    res = supabase.rpc('exec_sql', {'sql': 'SELECT 1'}).execute()
    print("SUCCESS: Result:", res.data)
except Exception as e:
    print("FAILED:", e)
