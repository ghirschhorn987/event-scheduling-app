import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    exit(1)

supabase: Client = create_client(url, key)
print("✅ Successfully imported Supabase client.\n")

def check_event_types():
    print("--- Checking Event Types ---")
    try:
        res = supabase.table("event_types").select("*").execute()
        
        if not res.data:
            print("No event types found.")
            return

        for et in res.data:
            print(f"ID: {et['id']}")
            print(f"  Name: {et['name']}")
            print(f"  Roster Group: {et.get('roster_user_group')}")
            print(f"  1st Priority Group: {et.get('reserve_first_priority_user_group')}")
            print(f"  2nd Priority Group: {et.get('reserve_second_priority_user_group')}")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error fetching event types: {e}")

if __name__ == "__main__":
    check_event_types()
