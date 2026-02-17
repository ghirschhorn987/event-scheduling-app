import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in backend/.env")
    exit(1)

MIGRATION_FILE = 'backend/database/migrations/move_duration_to_event_types.sql'

def run_migration():
    try:
        print(f"Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print(f"Reading migration file: {MIGRATION_FILE}")
        with open(MIGRATION_FILE, 'r') as f:
            sql_commands = f.read()
            
        print("Executing migration...")
        cur.execute(sql_commands)
        
        conn.commit()
        print("Migration executed successfully!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error executing migration: {e}")
        exit(1)

if __name__ == "__main__":
    run_migration()
