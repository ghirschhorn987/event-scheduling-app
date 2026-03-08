import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

test_uid = "98ef110a-e89d-4fc9-8429-0f1edf5b4bf0"
res = supabase.table("profiles").select("*, profile_groups(user_groups(*))").eq("auth_user_id", test_uid).maybe_single().execute()
print(res.data)
