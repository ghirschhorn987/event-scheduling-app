#!/usr/bin/env python3
"""
Quick script to check if database migrations have been applied.
Run from project root: python3 check_migration_status.py
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment from backend/.env
load_dotenv("backend/.env")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Cannot connect: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found")
    print("   Make sure backend/.env has these variables set")
    exit(1)

supabase = create_client(url, key)

print("=" * 60)
print("DATABASE SCHEMA VERIFICATION")
print("=" * 60)

migration_applied = True

# Check 1: profiles table has auth_user_id column
print("\n✓ Checking profiles.auth_user_id...")
try:
    res = supabase.table('profiles').select('id, email, auth_user_id').limit(1).execute()
    print("  ✅ Column EXISTS")
except Exception as e:
    if 'auth_user_id' in str(e):
        print("  ❌ Column MISSING - Migration NOT applied")
        migration_applied = False
    else:
        print(f"  ⚠️  Error: {e}")

# Check 2: profile_groups table exists
print("\n✓ Checking profile_groups table...")
try:
    res = supabase.table('profile_groups').select('*', count='exact').limit(1).execute()
    print(f"  ✅ Table EXISTS ({res.count} rows)")
except Exception as e:
    print("  ❌ Table MISSING - Migration NOT applied")
    migration_applied = False

# Check 3: profiles.user_group_id should be removed
print("\n✓ Checking if profiles.user_group_id removed...")
try:
    res = supabase.table('profiles').select('user_group_id').limit(1).execute()
    print("  ⚠️  Column STILL EXISTS (should be removed)")
    migration_applied = False
except Exception as e:
    if 'user_group_id' in str(e) or 'column' in str(e).lower():
        print("  ✅ Column removed (correct)")
    else:
        print(f"  ? Cannot verify: {e}")

print("\n" + "=" * 60)
if migration_applied:
    print("✅ MIGRATION APPLIED - Schema is up to date!")
else:
    print("❌ MIGRATION NOT APPLIED - Please run SQL scripts:")
    print("\n   1. Open Supabase SQL Editor")
    print("   2. Run: database/migration_decouple_profiles.sql")
    print("   3. Run: database/triggers.sql")
print("=" * 60)
