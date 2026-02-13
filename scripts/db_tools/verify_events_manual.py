import os
import requests
import json
from datetime import datetime

# Load .env manually
env_vars = {}
try:
    with open('backend/.env', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                k, v = line.split('=', 1)
                env_vars[k] = v
except FileNotFoundError:
    print("backend/.env not found")
    exit(1)

SUPABASE_URL = env_vars.get('SUPABASE_URL')
SUPABASE_KEY = env_vars.get('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing Supabase credentials")
    exit(1)

print(f"Checking events at {SUPABASE_URL}...")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Fetch all events
try:
    response = requests.get(f"{SUPABASE_URL}/rest/v1/events?select=*,event_types(*)", headers=headers)
    if response.status_code != 200:
        print(f"Error fetching events: {response.text}")
        exit(1)
    
    events = response.json()
    print(f"Found {len(events)} events.")
    
    now = datetime.utcnow().isoformat()
    print(f"Current UTC Time: {now}")
    
    for e in events:
        print(f"\nEvent ID: {e['id']}")
        print(f"  Name: {e.get('event_types', {}).get('name', 'Unknown')}")
        print(f"  Date: {e['event_date']}")
        print(f"  Status: {e['status']}")
        
except Exception as e:
    print(f"Exception: {e}")
