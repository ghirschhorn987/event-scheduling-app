-- Migration: Add description to user_groups and seed initial groups
-- Date: 2026-02-11

-- 1. Add description column to user_groups
ALTER TABLE user_groups ADD COLUMN IF NOT EXISTS description TEXT;

-- 2. Seed/Update User Groups
INSERT INTO user_groups (name, description)
VALUES 
  ('SuperAdmin', 'Has full unrestricted access to all parts of the system.'),
  ('Admin', 'Initially has the same access as SuperAdmin, but this may change in the future.'),
  ('FirstPriority', 'Used by certain system functionality to determine order among users (e.g., scheduling) — grants first priority.'),
  ('SecondaryPriority', 'Used by certain system functionality to determine order among users — grants second priority.'),
  ('BethAmAffiliated', 'Notes those users who have an affiliation with Beth Am.')
ON CONFLICT (name) DO UPDATE 
SET description = EXCLUDED.description;
