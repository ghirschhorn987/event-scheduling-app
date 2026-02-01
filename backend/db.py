from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Warning: SUPABASE_URL or SUPABASE_KEY not found in environment")

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    # Create a dummy client or set to None. 
    # For now, we'll just set it to None, but we need to handle this in main.py
    class DummyClient:
        def table(self, *args): raise Exception("Database not connected")
    supabase = DummyClient()
