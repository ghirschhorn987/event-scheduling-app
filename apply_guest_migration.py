import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

def apply_migration():
    statements = [
        "ALTER TABLE user_groups ADD COLUMN IF NOT EXISTS guest_limit INTEGER DEFAULT 0;",
        "ALTER TABLE event_signups ADD COLUMN IF NOT EXISTS is_guest BOOLEAN DEFAULT false;",
        "ALTER TABLE event_signups ADD COLUMN IF NOT EXISTS guest_name TEXT;",
        "ALTER TABLE event_signups DROP CONSTRAINT IF EXISTS event_signups_event_id_user_id_key;",
        "CREATE UNIQUE INDEX IF NOT EXISTS event_signups_user_only_idx ON event_signups (event_id, user_id) WHERE is_guest = false;"
    ]

    for stmt in statements:
        print(f"Executing: {stmt}")
        try:
             res = supabase.rpc("exec_sql", {"param": stmt}).execute()
             print("Success via exec_sql")
        except Exception as e:
            print(f"Failed via exec_sql: {e}")
            try:
                res = supabase.rpc("sql", {"query": stmt}).execute()
                print("Success via sql RPC")
            except Exception as e2:
                print(f"Failed via sql RPC: {e2}")

if __name__ == "__main__":
    apply_migration()
