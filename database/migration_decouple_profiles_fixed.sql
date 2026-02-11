-- Migration: Decouple profiles from auth.users (Enable Pre-provisioning)
-- CORRECTED VERSION - Adds email column before adding constraints

-- 1. Add missing EMAIL column to profiles table
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email TEXT;

-- 2. Add auth_user_id column
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS auth_user_id UUID REFERENCES auth.users(id);

-- 3. Backfill auth_user_id for existing users (assuming id was the auth_id)
UPDATE profiles SET auth_user_id = id WHERE auth_user_id IS NULL;

-- 4. Add constraint unique auth_user_id (drop first if exists)
DO $$ 
BEGIN
  ALTER TABLE profiles ADD CONSTRAINT profiles_auth_user_id_key UNIQUE (auth_user_id);
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

-- 5. Make Email Unique (critical for linking)
DO $$ 
BEGIN
  ALTER TABLE profiles ADD CONSTRAINT profiles_email_key UNIQUE (email);
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

-- 6. Drop Foreign Key connection on ID (It is no longer strictly auth.users.id)
-- First drop the FK constraint. Constraint name usually profiles_id_fkey
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;

-- 7. Change ID default to gen_random_uuid() if it's not already
ALTER TABLE profiles ALTER COLUMN id SET DEFAULT gen_random_uuid();

-- 8. Drop user_group_id (We are moving to Many-to-Many)
ALTER TABLE profiles DROP COLUMN IF EXISTS user_group_id;


-- 9. Ensure PROFILE_GROUPS table exists (Many-to-Many)
CREATE TABLE IF NOT EXISTS profile_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  user_group_id UUID REFERENCES user_groups(id) ON DELETE CASCADE NOT NULL,
  UNIQUE(profile_id, user_group_id)
);

ALTER TABLE profile_groups ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if it exists
DROP POLICY IF EXISTS "Profile Groups viewable by everyone" ON profile_groups;
CREATE POLICY "Profile Groups viewable by everyone" ON profile_groups FOR SELECT USING (true);


-- 10. Update RLS on Profiles
-- Old: auth.uid() = id
-- New: auth.uid() = auth_user_id
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile" ON profiles 
  FOR UPDATE USING (auth.uid() = auth_user_id);

-- PUBLIC READ IS ALREADY THERE ("Public profiles are viewable by everyone")
