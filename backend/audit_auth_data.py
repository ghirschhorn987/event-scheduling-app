import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

url: str = os.environ.get("SUPABASE_URL")
# MUST use service role key to access auth.users via admin API
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found.")
    exit(1)

supabase = create_client(url, key)

def run_audit():
    print("--- Starting Data Integrity & Auth Audit ---")
    
    # 1. Fetch all auth users
    # Note: supabase-py admin api is available under supabase.auth.admin
    try:
        # Note: If there are more than 50 users, we might need pagination.
        # list_users() returns a list of User objects (or dicts).
        response = supabase.auth.admin.list_users()
        auth_users = response.users if hasattr(response, 'users') else response
    except Exception as e:
        print(f"Error fetching auth users: {e}")
        return

    # 2. Fetch all public profiles
    try:
        profiles_res = supabase.table("profiles").select("*").execute()
        profiles = profiles_res.data
    except Exception as e:
        print(f"Error fetching profiles: {e}")
    # 3. Fetch all registration requests
    try:
        requests_res = supabase.table("registration_requests").select("*").execute()
        requests_data = requests_res.data
    except Exception as e:
        print(f"Error fetching registration requests: {e}")
        return

    print(f"Found {len(auth_users)} auth records, {len(profiles)} profile records, and {len(requests_data)} registration requests.\n")

    auth_dict = {u.id if hasattr(u, 'id') else u['id']: u for u in auth_users}
    
    # helper for auth emails
    auth_email_dict = {}
    for uid, u in auth_dict.items():
        if isinstance(u, dict):
            u_email = u.get('email', '').lower()
        else:
            u_email = getattr(u, 'email', '').lower()
        if u_email:
            auth_email_dict[u_email] = u

    profile_dict = {p['auth_user_id']: p for p in profiles}
    profile_email_dict = {p.get('email', '').lower(): p for p in profiles if p.get('email')}
    request_email_dict = {r.get('email', '').lower(): r for r in requests_data if r.get('email')}

    # Audit for mismatches
    print("--- Auditing Mismatches ---")
    missing_profiles = []
    missing_auth = []

    for auth_id in auth_dict:
        if auth_id not in profile_dict:
            if isinstance(auth_dict[auth_id], dict):
                u_email = auth_dict[auth_id].get('email', 'Unknown')
            else:
                u_email = getattr(auth_dict[auth_id], 'email', 'Unknown')
            missing_profiles.append({"id": auth_id, "email": u_email})

    for profile in profiles:
        auth_id = profile.get('auth_user_id')
        if not auth_id or auth_id not in auth_dict:
            missing_auth.append(profile)

    if missing_profiles:
        print(f"WARNING: {len(missing_profiles)} Auth users missing a profile:")
        for mp in missing_profiles:
            print(f"  - {mp['email']} (ID: {mp['id']})")
    else:
        print("OK: All auth users have a corresponding profile.")

    if missing_auth:
        print(f"WARNING: {len(missing_auth)} Profiles missing an active auth record:")
        for ma in missing_auth:
            print(f"  - {ma.get('email')} / {ma.get('name')} (Profile ID: {ma.get('id')}, linked Auth ID: {ma.get('auth_user_id')})")
    else:
        print("OK: All profiles map to a valid auth user.")

    print("\n--- Auditing Registration Requests ---")
    
    approved_missing_profile = []
    pending_with_profile = []
    
    for req in requests_data:
        r_email = req.get('email', '').lower()
        status = req.get('status')
        
        has_profile = r_email in profile_email_dict
        
        if status == 'APPROVED' and not has_profile:
            approved_missing_profile.append(req)
        elif status in ['PENDING', 'DECLINED', 'INFO_NEEDED'] and has_profile:
            pending_with_profile.append(req)
            
    if approved_missing_profile:
        print(f"WARNING: {len(approved_missing_profile)} APPROVED requests are missing a Profile:")
        for req in approved_missing_profile:
            print(f"  - {req.get('email')} (Request ID: {req.get('id')})")
    else:
        print("OK: All approved requests have a corresponding Profile.")
        
    if pending_with_profile:
        print(f"WARNING: {len(pending_with_profile)} Non-approved requests HAVE a Profile:")
        for req in pending_with_profile:
             print(f"  - {req.get('email')} (Status: {req.get('status')})")
    else:
        print("OK: No pending/declined requests have leaked Profiles.")

    # Also check if any profile exists WITHOUT a registration request
    # This is often expected for Admin/Bulk Imported users, but good to log
    profiles_without_request = []
    for p_email in profile_email_dict:
        if p_email not in request_email_dict:
            profiles_without_request.append(p_email)
            
    if profiles_without_request:
        print(f"INFO: {len(profiles_without_request)} Profiles exist with NO registration request (Likely bulk imported):")
        for p in profiles_without_request:
            print(f"  - {p}")

    print("\n--- Auditing Duplicates ---")
    email_counts = {}
    name_counts = {}

    for p in profiles:
        e = p.get('email', '').lower()
        n = p.get('name', '').lower()
        if e: email_counts[e] = email_counts.get(e, 0) + 1
        if n: name_counts[n] = name_counts.get(n, 0) + 1

    dup_emails = {k: v for k, v in email_counts.items() if v > 1}
    dup_names = {k: v for k, v in name_counts.items() if v > 1}

    if dup_emails:
        print(f"WARNING: Found {len(dup_emails)} duplicate emails:")
        for email, count in dup_emails.items():
            print(f"  - {email}: {count} profiles")
    else:
        print("OK: No duplicate emails found in profiles.")

    if dup_names:
        print(f"WARNING: Found {len(dup_names)} duplicate names:")
        for name, count in dup_names.items():
            print(f"  - {name}: {count} profiles")
    else:
        print("OK: No duplicate names found in profiles.")


    print("\n--- Backfilling Auth Methods ---")
    updated_count = 0
    skipped_count = 0
    error_count = 0

    for profile in profiles:
        auth_id = profile.get('auth_user_id')
        if not auth_id or auth_id not in auth_dict:
            skipped_count += 1
            continue

        # Check existing method
        existing_method = profile.get('auth_method')
        if existing_method:
            skipped_count += 1
            continue
        
        auth_user = auth_dict[auth_id]
        
        # Supabase Python SDK User object: app_metadata is typically a dict attribute
        if isinstance(auth_user, dict):
            app_metadata = auth_user.get('app_metadata', {})
        else:
            app_metadata = getattr(auth_user, 'app_metadata', {})
            if app_metadata is None:
                app_metadata = {}
        
        auth_method = 'email' # default
        
        # app_metadata typically has a "providers" list
        providers = app_metadata.get('providers', []) if isinstance(app_metadata, dict) else []
        if 'google' in providers:
            auth_method = 'google'
        elif isinstance(app_metadata, dict) and app_metadata.get('provider') == 'google':
             auth_method = 'google'

        print(f"Updating {profile.get('email')} -> {auth_method}")
        try:
            supabase.table("profiles").update({"auth_method": auth_method}).eq("id", profile['id']).execute()
            updated_count += 1
        except Exception as e:
            print(f"  Error updating profile {profile['id']}: {e}")
            error_count += 1

    print("\n--- Summary ---")
    print(f"Successfully updated auth_method for {updated_count} profiles.")
    print(f"Skipped {skipped_count} profiles (already set or missing auth).")
    if error_count > 0:
        print(f"Failed to update {error_count} profiles.")

if __name__ == "__main__":
    run_audit()
