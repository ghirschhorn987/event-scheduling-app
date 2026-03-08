# Blocker Log

**Phase 5: Authentication & Data Audit**
- Skipped performing the audit on Supabase tables for duplicates/inconsistencies as a one-off database script is needed which is out of present scope.
- Skipped adding "User Education/Switching" tips as there isn't actually a proper "User Profile" page for non-admin users where this could logically be placed yet.
- Skipped showing "Auth Method Indication" because auth method details exist only on `auth.users` schema and would require complex joining logic or a background trigger to copy to `public.profiles`.
