import os
import psycopg2
from dotenv import load_dotenv

load_dotenv("backend/.env")

# Supabase Postgres Connection String
# "postgres://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
# We need the DB password. It is NOT in .env (usually).
# The user might have provided it or I might need to ask.
# Wait, I see `SUPABASE_KEY` (Service Role).
# I can use the Supabase Client to execute SQL *IF* there is a function for it, or if I use the REST API to call 'rpc'?
# But standardized SQL execution via REST is not default.
#
# Alternative: The user typically runs migrations via CLI or checking the dashboard.
# But I need to do it.
#
# I will try to use the `postgres` connection string if I can find the password.
# If not, I can try to use the `supabase` python client to run a stored procedure if one exists...
#
# Actually, I can use the `supabase-cli` if installed?
# `supabase db push`?
#
# Let's check if `psycopg2` is installed.
# And check `.env` for DB_PASSWORD.

try:
    import psycopg2
    print("psycopg2 is installed.")
except ImportError:
    print("psycopg2 is NOT installed.")

# Check env
db_url = os.environ.get("DATABASE_URL")
if db_url:
    print("DATABASE_URL found.")
else:
    print("DATABASE_URL NOT found in .env.")

# Basic Migration Runner
def run_migration():
    if not db_url:
        print("Cannot run migration without DATABASE_URL.")
        return

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        with open("database/migration_refactor_events.sql", "r") as f:
            sql = f.read()
            
        cur.execute(sql)
        conn.commit()
        print("Migration successful.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
