-- Migration: Disable Automatic Profile Creation
-- This ensures that new users who sign in with Google do not immediately get a profile/access.
-- They must go through the Registration process and be approved by an Admin.

-- 1. Drop the trigger that auto-creates profiles
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- 2. Drop the function (optional, but cleaner)
DROP FUNCTION IF EXISTS public.handle_new_user();

-- Note: Existing users are not affected. 
-- New users will now have an entry in auth.users upon Google Sign-In, 
-- but NO entry in public.profiles.
-- This will cause the frontend AccessControl check to fail, blocking access as desired.
