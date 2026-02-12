
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

def try_exec_sql():
    sql = "ALTER TABLE event_signups ADD COLUMN IF NOT EXISTS tier INTEGER;"
    print(f"Attempting to execute via RPC exec_sql: {sql}")
    try:
        # Some setups have this
        res = supabase.rpc("exec_sql", {"param": sql}).execute()
        print("Success:", res)
    except Exception as e:
        print("RPC 'exec_sql' failed:", e)
        
    try:
        # Some setups have it as just 'sql'
        res = supabase.rpc("sql", {"query": sql}).execute()
        print("Success:", res)
    except Exception as e:
        print("RPC 'sql' failed:", e)

if __name__ == "__main__":
    try_exec_sql()
