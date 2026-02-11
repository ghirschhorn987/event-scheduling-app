-- Refactor User Management Schema

-- 1. Update user_groups table
ALTER TABLE user_groups ADD COLUMN IF NOT EXISTS google_group_id TEXT;

-- 2. Create profile_groups join table
CREATE TABLE IF NOT EXISTS profile_groups (
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    group_id UUID REFERENCES user_groups(id) ON DELETE CASCADE,
    PRIMARY KEY (profile_id, group_id)
);

-- 3. Update profiles table
-- We drop email because it's in auth.users
-- We drop user_group_id because we use the join table now
ALTER TABLE profiles DROP COLUMN IF EXISTS email;
ALTER TABLE profiles DROP COLUMN IF EXISTS user_group_id;

-- 4. Seed default groups
-- We use ON CONFLICT DO NOTHING to avoid errors if they exist, 
-- but since we might wipe data later, this is safe.
INSERT INTO user_groups (name) VALUES ('Super Admin') ON CONFLICT (name) DO NOTHING;
INSERT INTO user_groups (name) VALUES ('Admin') ON CONFLICT (name) DO NOTHING;
INSERT INTO user_groups (name) VALUES ('Primary') ON CONFLICT (name) DO NOTHING;
INSERT INTO user_groups (name) VALUES ('Secondary') ON CONFLICT (name) DO NOTHING;
