import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("backend/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)

# Fetch all events with their types
response = supabase.table("events").select("*, event_types(name)").order("event_date").execute()

print(f"\n=== Total Events: {len(response.data)} ===\n")

for event in response.data:
    event_name = event['event_types']['name']
    event_date = event['event_date']
    status = event['status']
    print(f"{event_name:25} | {event_date} | {status}")
