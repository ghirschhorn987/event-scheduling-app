import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(url, key)

emails = [
    "liliagh@gmail.com",
    "admin@skeddle.net",
    "bmbachrach@gmail.com",
    "geehirschh99@gmail.com"
]

def check_accounts():
    print("--- Diagnostic: Checking Accounts ---\n")
    
    # 1. Check profiles
    print("Checking Profiles Table:")
    for email in emails:
        res = supabase.table("profiles").select("id, email, name, auth_user_id").eq("email", email).execute()
        if res.data:
            p = res.data[0]
            print(f"  {email}: ProfileID={p['id']}, AuthUserID={p['auth_user_id']}")
        else:
            print(f"  {email}: NO PROFILE FOUND")
            
    # 2. Check Auth Users
    print("\nChecking Supabase Auth (Admin API):")
    try:
        response = supabase.auth.admin.list_users()
        auth_users = response.users if hasattr(response, 'users') else response
        auth_email_map = {u.email.lower(): u for u in auth_users if u.email}
        
        print(f"Total Auth Users: {len(auth_users)}")
        print("All Auth Emails (excluding mocks):")
        for email_addr in sorted(auth_email_map.keys()):
            if not email_addr.endswith('@test.com'):
                print(f"  - {email_addr}")

        print("\nChecking Specific Emails:")
        for email in emails:
            if email.lower() in auth_email_map:
                u = auth_email_map[email.lower()]
                print(f"  {email}: AUTH USER FOUND! ID={u.id}")
            else:
                print(f"  {email}: NO AUTH USER FOUND")
    except Exception as e:
        print(f"Error checking auth: {e}")

    # 3. Check Registration Requests
    print("\nChecking Registration Requests:")
    for email in emails:
        res = supabase.table("registration_requests").select("id, email, status").eq("email", email).execute()
        if res.data:
            r = res.data[0]
            print(f"  {email}: RequestID={r['id']}, Status={r['status']}")
        else:
            # Try a fuzzy match for the typo case
            if "geehirschh99" in email:
                fuzzy = supabase.table("registration_requests").select("id, email, status").ilike("email", "%geehirsch%").execute()
                if fuzzy.data:
                    for f in fuzzy.data:
                        print(f"  {email}: FUZZY MATCH FOUND: {f['email']} (Status={f['status']})")
                else:
                    print(f"  {email}: NO REQUEST FOUND")
            else:
                print(f"  {email}: NO REQUEST FOUND")

if __name__ == "__main__":
    check_accounts()
