
import os
import sys

# Add backend directory to path so we can import db
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from db import supabase
except ImportError:
    print("Could not import supabase client. Make sure you are running this from the project root.")
    sys.exit(1)

def list_users_and_groups():
    print("Fetching profiles and user groups...")
    
    # query profiles and their groups
    # based on main.py logic: profiles -> profile_groups -> user_groups
    # BUT wait, schema.sql (line 16) says profiles has a user_group_id directly? 
    # Let's check schema again. 
    # schema.sql line 16: user_group_id UUID REFERENCES user_groups(id)
    # BUT main.py line 81: .select("*, profile_groups(user_groups(name))")
    # This suggests there is a many-to-many join table `profile_groups` getting used in the app, 
    # OR the schema in schema.sql is outdated/different from what logic expects.
    # main.py seems to be the source of truth for the *running* code.
    
    # Let's try both paths to be sure.
    
    try:
        # Path A: Many-to-Many via profile_groups (as seen in main.py)
        res = supabase.table("profiles").select("*, profile_groups(user_groups(name))").execute()
        
        print(f"\nFound {len(res.data)} profiles.")
        
        print(f"{'Name':<30} | {'Email':<30} | {'Groups'}")
        print("-" * 80)
        
        for p in res.data:
            name = p.get("name", "N/A")
            email = p.get("email", "N/A") # Might be empty if removed
            
            groups = []
            # Check profile_groups
            if p.get("profile_groups"):
                for pg in p["profile_groups"]:
                    if pg.get("user_groups"):
                        groups.append(pg["user_groups"]["name"])
            
            # Check direct user_group_id if it exists and wasn't caught above
            # (We would need to fetch user_groups separately to map ID to name if we relied on this)
            
            group_str = ", ".join(groups) if groups else "None"
            print(f"{name:<30} | {email:<30} | {group_str}")
            
    except Exception as e:
        print(f"Error querying with profile_groups: {e}")
        print("Trying direct user_group_id...")
        
        # Path B: Direct user_group_id (as seen in schema.sql)
        try:
            res = supabase.table("profiles").select("*, user_groups(name)").execute()
            print(f"\nFound {len(res.data)} profiles (Direct FK).")
             
            print(f"{'Name':<30} | {'Email':<30} | {'Groups'}")
            print("-" * 80)
            
            for p in res.data:
                name = p.get("name", "N/A")
                email = p.get("email", "N/A")
                
                group_name = "None"
                if p.get("user_groups"):
                    group_name = p["user_groups"]["name"]
                
                print(f"{name:<30} | {email:<30} | {group_name}")
                
        except Exception as e2:
             print(f"Error querying with direct FK: {e2}")

if __name__ == "__main__":
    list_users_and_groups()
