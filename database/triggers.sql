-- Trigger to link a pre-provisioned profile when a new auth user is created
-- Run this in your Supabase SQL Editor
--
-- NOTE: This trigger is a best-effort optimization. The primary linking 
-- mechanism is the backend fallback in get_current_user() which repairs
-- unlinked profiles at login time. This is necessary because AFTER INSERT
-- triggers on auth.users are unreliable for Google OAuth signups.

-- 1. Create a function that handles the new user
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
DECLARE
  existing_profile_id UUID;
BEGIN
  -- Check if a profile already exists for this email (Pre-provisioned)
  SELECT id INTO existing_profile_id FROM public.profiles WHERE email = new.email;

  IF existing_profile_id IS NOT NULL THEN
    -- Link existing profile to this new Auth User
    UPDATE public.profiles
    SET auth_user_id = new.id
    WHERE id = existing_profile_id;
  END IF;
  -- If no profile found, do nothing. The user will either:
  -- 1. Get linked via the backend fallback on next login
  -- 2. Get blocked by the backend if they were never approved

  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Create the trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
