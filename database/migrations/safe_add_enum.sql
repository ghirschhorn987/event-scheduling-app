-- Safe Enum Update Script
-- Copy and run this entire block in Supabase SQL Editor

DO $$
BEGIN
    ALTER TYPE event_status ADD VALUE 'NOT_YET_OPEN';
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$
BEGIN
    ALTER TYPE event_status ADD VALUE 'OPEN_FOR_ROSTER';
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$
BEGIN
    ALTER TYPE event_status ADD VALUE 'OPEN_FOR_RESERVES';
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$
BEGIN
    ALTER TYPE event_status ADD VALUE 'PRELIMINARY_ORDERING';
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$
BEGIN
    ALTER TYPE event_status ADD VALUE 'FINAL_ORDERING';
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$
BEGIN
    ALTER TYPE event_status ADD VALUE 'FINISHED';
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- CANCELLED is likely already there, but safe to check
DO $$
BEGIN
    ALTER TYPE event_status ADD VALUE 'CANCELLED';
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
