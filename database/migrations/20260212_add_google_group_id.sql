-- Migration: Add google_group_id to user_groups
-- Date: 2026-02-12

ALTER TABLE user_groups ADD COLUMN IF NOT EXISTS google_group_id TEXT;
