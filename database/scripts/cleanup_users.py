import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv("backend/.env")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_SERVICE_KEY:
    print("Error: SUPABASE_SERVICE_ROLE_KEY is required to delete users.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

import argparse

def cleanup_orphaned_users(assume_yes=False):
    """
    Identifies and deletes users in auth.users who do not have a linked profile.
    """
    print("Fetching auth users...")
    # List users (requires service role)
    users_res = supabase.auth.admin.list_users()
    all_users = users_res
    
    print(f"Found {len(all_users)} users in auth.users")
    
    # Fetch all emails in profiles
    profiles_res = supabase.table("profiles").select("email").execute()
    approved_emails = {p['email'] for p in profiles_res.data}
    
    print(f"Found {len(approved_emails)} approved profiles.")
    
    orphans = []
    for user in all_users:
        if user.email not in approved_emails:
            orphans.append(user)

    if not orphans:
        print("No orphaned users found.")
        return

    print(f"Found {len(orphans)} orphaned users:")
    for u in orphans:
        print(f" - {u.email} ({u.id})")

    if not assume_yes:
        confirm = input(f"\nProceed to delete these {len(orphans)} users? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            return

    for u in orphans:
        print(f"Deleting {u.email}...")
        try:
            supabase.auth.admin.delete_user(u.id)
            print("  -> Deleted.")
        except Exception as e:
            print(f"  -> Failed to delete: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleanup orphaned auth users.")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt.")
    args = parser.parse_args()
    
    cleanup_orphaned_users(assume_yes=args.yes)
