-- Migration: Add group_email to user_groups
ALTER TABLE user_groups ADD COLUMN group_email TEXT;
