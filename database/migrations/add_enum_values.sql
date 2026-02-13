-- Run this in your Supabase SQL Editor to update the enum
BEGIN;
  -- Postgres < 12 does not support IF NOT EXISTS for ALTER TYPE
  -- If you get an error that value exists, you can ignore it or remove that line.
  
  ALTER TYPE event_status ADD VALUE 'NOT_YET_OPEN';
EXCEPTION
  WHEN duplicate_object THEN null;
END;

BEGIN;
  ALTER TYPE event_status ADD VALUE 'OPEN_FOR_ROSTER';
EXCEPTION
  WHEN duplicate_object THEN null;
END;

BEGIN;
  ALTER TYPE event_status ADD VALUE 'OPEN_FOR_RESERVES';
EXCEPTION
  WHEN duplicate_object THEN null;
END;

BEGIN;
  ALTER TYPE event_status ADD VALUE 'PRELIMINARY_ORDERING';
EXCEPTION
  WHEN duplicate_object THEN null;
END;

BEGIN;
  ALTER TYPE event_status ADD VALUE 'FINAL_ORDERING';
EXCEPTION
  WHEN duplicate_object THEN null;
END;

BEGIN;
  ALTER TYPE event_status ADD VALUE 'FINISHED';
EXCEPTION
  WHEN duplicate_object THEN null;
END;

BEGIN;
  ALTER TYPE event_status ADD VALUE 'CANCELLED';
EXCEPTION
  WHEN duplicate_object THEN null;
END;

-- Actually, standard Postgres block structure might not work in simple SQL editor without DO block.
-- Simpler approach:
-- ALTER TYPE event_status ADD VALUE 'NOT_YET_OPEN';
-- ...
-- But if it exists it fails.
-- Better to use a DO block

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

DO $$
BEGIN
    ALTER TYPE event_status ADD VALUE 'CANCELLED';
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
