import os
import sys
import psycopg2
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load .env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", ".env")
load_dotenv(env_path)

DATABASE_URL = os.environ.get("DATABASE_URL")

# Try frontend .env if backend failed (common issue in this env)
if not DATABASE_URL:
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", ".env")
    load_dotenv(env_path)
    # VITE_SUPABASE_URL is not DATABASE_URL. We need the direct connection string for psycopg2.
    # The user might NOT have DATABASE_URL in .env if they are using Supabase client only.
    # But `deploy.sh` implies they have `SUPABASE_SERVICE_ROLE_KEY`.
    # I cannot use psycopg2 without a connection string (postgres://user:pass@host...).
    # Supabase usually provides this in the dashboard, but maybe not in the repo .env.
    
    # If I can't connect via psycopg2, I can't check directly easily unless I use the REST API to call a function?
    # Or just try to insert a dummy row?
    pass

def check_enum():
    if not os.environ.get("DATABASE_URL"):
        print("DATABASE_URL not found. Cannot check Enum directly via psycopg2.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT enum_range(NULL::event_status)")
        print(f"Current Enum Values: {cur.fetchone()[0]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error checking enum: {e}")

if __name__ == "__main__":
    check_enum()
