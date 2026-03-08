import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

res = supabase.table("user_groups").select("*").limit(1).execute()
print(res.data)
