-- Add auth_method column to profiles table
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS auth_method text;

-- Reload schema cache to ensure PostgREST picks up the new column immediately
NOTIFY pgrst, reload_schema;
