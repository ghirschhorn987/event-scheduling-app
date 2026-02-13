import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

def apply_migration():
    with open("migrations/update_event_status.sql", "r") as f:
        sql = f.read()
    
    # Split by STATEMENT if possible, but RPC `exec_sql` usually handles blocks.
    # However, `ALTER TYPE` cannot run inside a transaction block in some contexts.
    # Let's try running it.
    
    print("Applying migration...")
    # We might need to run these individually if it fails as a block
    statements = [
        "ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'NOT_YET_OPEN';",
        "ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'OPEN_FOR_ROSTER';",
        "ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'OPEN_FOR_RESERVES';",
        "ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'PRELIMINARY_ORDERING';",
        "ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'FINAL_ORDERING';",
        "ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'FINISHED';",
        "UPDATE events SET status = 'NOT_YET_OPEN' WHERE status = 'SCHEDULED';"
    ]

    for stmt in statements:
        print(f"Executing: {stmt}")
        try:
             # Try exec_sql RPC
             res = supabase.rpc("exec_sql", {"param": stmt}).execute()
             print("Success")
        except Exception as e:
            print(f"Failed via exec_sql: {e}")
            # Try 'sql' RPC (sometimes enabled)
            try:
                res = supabase.rpc("sql", {"query": stmt}).execute()
                print("Success via sql RPC")
            except Exception as e2:
                print(f"Failed via sql RPC: {e2}")

if __name__ == "__main__":
    apply_migration()
