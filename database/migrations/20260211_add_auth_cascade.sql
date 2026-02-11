-- Add ON DELETE CASCADE to the foreign key between profiles and auth.users
-- This ensures that when an auth.users record is deleted, the corresponding profile is also deleted.

-- 1. Identify and drop the existing constraint (if it exists)
-- Note: Based on migration_decouple_profiles_fixed.sql, it might not have been named explicitly.
-- We'll use a standard name or look it up.
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'profiles_auth_user_id_fkey') THEN
        ALTER TABLE public.profiles DROP CONSTRAINT profiles_auth_user_id_fkey;
    END IF;
END $$;

-- 2. Re-add with CASCADE
ALTER TABLE public.profiles
ADD CONSTRAINT profiles_auth_user_id_fkey 
FOREIGN KEY (auth_user_id) 
REFERENCES auth.users(id) 
ON DELETE CASCADE;
