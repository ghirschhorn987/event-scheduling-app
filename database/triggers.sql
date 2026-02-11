-- Trigger to create a profile when a new user signs up
-- Run this in your Supabase SQL Editor

-- 1. Create a function that handles the new user
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
DECLARE
  existing_profile_id UUID;
BEGIN
  -- 1. Check if a profile already exists for this email (Pre-provisioned)
  SELECT id INTO existing_profile_id FROM public.profiles WHERE email = new.email;

  IF existing_profile_id IS NOT NULL THEN
    -- Link existing profile to this new Auth User
    UPDATE public.profiles
    SET auth_user_id = new.id
    WHERE id = existing_profile_id;
  ELSE
    -- No pre-provisioned profile found.
    -- HARD BLOCK: Prevent auth.users record from being created.
    RAISE EXCEPTION 'ACCESS_DENIED: This email has not been approved for access. Please request access at /request-access';
  END IF;

  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Create the trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
