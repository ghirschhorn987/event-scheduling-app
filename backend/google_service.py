import os
from typing import List, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from db import supabase

# Scopes required for managing Admin SDK Groups
SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.group.member'
]

def get_google_service():
    """Builds and returns the Admin SDK Directory service."""
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    admin_email = os.environ.get("GOOGLE_ADMIN_EMAIL")

    if not creds_path or not os.path.exists(creds_path):
        raise ValueError(f"Google credentials file not found at path: {creds_path}. Please set GOOGLE_APPLICATION_CREDENTIALS.")

    if not admin_email:
        raise ValueError("GOOGLE_ADMIN_EMAIL environment variable is not set. Please set it to your workspace admin email.")

    # Load credentials from file
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )
    
    # Delegate as the domain admin
    creds = creds.with_subject(admin_email)
    
    return build('admin', 'directory_v1', credentials=creds)

def get_google_members(service, google_group_email: str) -> List[str]:
    """Fetches all member emails for a given Google Group."""
    members = []
    page_token = None
    
    while True:
        try:
            results = service.members().list(
                groupKey=google_group_email,
                pageToken=page_token
            ).execute()
            
            for member in results.get('members', []):
                members.append(member.get('email'))
                
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        except Exception as e:
            # Group might not exist or no permission
            raise ValueError(f"Error fetching members from {google_group_email}: {str(e)}")
            
    return members

async def sync_to_google(group_id: str) -> Dict[str, Any]:
    """
    Syncs a Supabase user group to its corresponding Google Group.
    """
    try:
        # 1. Fetch group details
        group_res = supabase.table("user_groups").select("*").eq("id", group_id).execute()
        if not group_res.data:
            return {"status": "error", "message": "Group not found"}
        
        group = group_res.data[0]
        group_name = group.get("name")
        google_group_email = group.get("group_email")
        
        if not google_group_email:
            return {"status": "error", "message": f"Group '{group_name}' does not have a Google Group Email assigned in Supabase."}

        # 2. Fetch Supabase members (Ground Truth)
        members_res = supabase.table("profile_groups")\
            .select("profiles(email)")\
            .eq("group_id", group_id)\
            .execute()
        
        supabase_emails = set()
        if members_res.data:
            for m in members_res.data:
                profile = m.get("profiles")
                if profile and profile.get("email"):
                    supabase_emails.add(profile["email"].lower())

        # 3. Authenticate and build Google Service
        try:
            service = get_google_service()
        except ValueError as ve:
            return {"status": "error", "message": str(ve)}

        # 4. Fetch Current Google Members
        try:
            google_members_list = get_google_members(service, google_group_email)
            google_emails = set(email.lower() for email in google_members_list if email)
        except Exception as e:
            return {"status": "error", "message": str(e)}

        # 5. Calculate Delta
        to_add = list(supabase_emails - google_emails)
        to_remove = list(google_emails - supabase_emails)

        # 6. Apply Actions to Google Groups
        for email in to_add:
            try:
                service.members().insert(
                    groupKey=google_group_email,
                    body={"email": email, "role": "MEMBER"}
                ).execute()
                print(f"[+] Added {email} to {google_group_email}")
            except Exception as e:
                print(f"[!] Failed to add {email} to {google_group_email}: {str(e)}")

        for email in to_remove:
            try:
                service.members().delete(
                    groupKey=google_group_email,
                    memberKey=email
                ).execute()
                print(f"[-] Removed {email} from {google_group_email}")
            except Exception as e:
                print(f"[!] Failed to remove {email} from {google_group_email}: {str(e)}")

        return {
            "status": "success",
            "group_name": group_name,
            "added": to_add,
            "removed": to_remove,
            "summary": f"Sync Complete: Added {len(to_add)}, Removed {len(to_remove)}"
        }
    except Exception as e:
        print(f"Error syncing group to Google: {e}")
        return {"status": "error", "message": str(e)}
