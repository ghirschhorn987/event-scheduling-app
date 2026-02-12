import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from db import supabase

def check_schema():
    print("=" * 60)
    print("DATABASE SCHEMA VERIFICATION")
    print("=" * 60)
    
    # Check 1: profiles table has auth_user_id column
    print("\n1. Checking profiles table for 'auth_user_id' column...")
    try:
        res = supabase.table('profiles').select('id, email, auth_user_id').limit(1).execute()
        print("   ✅ 'auth_user_id' column EXISTS in profiles table")
        if res.data:
            print(f"   Sample: {res.data[0]}")
    except Exception as e:
        if 'auth_user_id' in str(e) or 'column' in str(e).lower():
            print("   ❌ 'auth_user_id' column MISSING - Migration NOT applied")
        else:
            print(f"   ❌ Error: {e}")
    
    # Check 2: profiles table has email column with unique constraint
    print("\n2. Checking profiles table for 'email' column...")
    try:
        res = supabase.table('profiles').select('email').limit(1).execute()
        print("   ✅ 'email' column EXISTS in profiles table")
    except Exception as e:
        print(f"   ❌ 'email' column MISSING - Migration NOT applied")
        print(f"   Error: {e}")
    
    # Check 3: profile_groups table exists
    print("\n3. Checking for 'profile_groups' table...")
    try:
        res = supabase.table('profile_groups').select('*', count='exact').limit(1).execute()
        print(f"   ✅ 'profile_groups' table EXISTS (count: {res.count})")
        if res.data:
            print(f"   Sample: {res.data[0]}")
    except Exception as e:
        print("   ❌ 'profile_groups' table MISSING - Migration NOT applied")
        print(f"   Error: {e}")
    
    # Check 4: Check if profiles has user_group_id (should be removed)
    print("\n4. Checking if old 'user_group_id' column was removed...")
    try:
        res = supabase.table('profiles').select('user_group_id').limit(1).execute()
        print("   ⚠️  'user_group_id' column STILL EXISTS - Migration incomplete")
    except Exception as e:
        if 'user_group_id' in str(e) or 'column' in str(e).lower():
            print("   ✅ 'user_group_id' column removed (as expected)")
        else:
            print(f"   ? Unable to verify: {e}")

    # Check 5: Check if event_signups has tier column
    print("\n5. Checking event_signups table for 'tier' column...")
    try:
        res = supabase.table('event_signups').select('tier').limit(1).execute()
        print("   ✅ 'tier' column EXISTS in event_signups table")
    except Exception as e:
        print(f"   ❌ 'tier' column MISSING in event_signups table")
        print(f"   Error: {e}")    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nIf all checks passed (✅), the migration has been applied.")
    print("If any checks failed (❌), you need to run the migration scripts.")
    print("\nMigration files to run in Supabase SQL Editor:")
    print("  1. database/migration_decouple_profiles.sql")
    print("  2. database/triggers.sql")
    print("=" * 60)

if __name__ == "__main__":
    check_schema()
