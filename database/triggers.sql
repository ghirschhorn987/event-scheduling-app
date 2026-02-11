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
    
    -- Optionally update name if it was missing?
    -- UPDATE public.profiles SET name = ... WHERE ...
  ELSE
    -- No pre-provisioned profile found.
    -- Option A: Create a 'Guest' profile?
    -- Option B: Do nothing (User has no profile, thus no access).
    -- Given the requirements "Admin approves -> Profile created", 
    -- if they signup *without* approval, they shouldn't get a profile.
    -- However, legacy behavior allowed signup. 
    -- Let's NOT create a profile here. If they aren't pre-provisioned, they have to request access.
    
    -- Logging (optional)
    -- RAISE NOTICE 'User signed up without pre-provisioned profile: %', new.email;
    NULL;
  END IF;

  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Create the trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
