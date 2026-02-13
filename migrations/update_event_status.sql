-- 1. Add new enum values
-- Postgres doesn't support adding multiple values in one command easily within a transaction block in some versions, 
-- but we can do them one by one.
ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'NOT_YET_OPEN';
ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'OPEN_FOR_ROSTER';
ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'OPEN_FOR_RESERVES';
ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'PRELIMINARY_ORDERING';
ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'FINAL_ORDERING';
ALTER TYPE event_status ADD VALUE IF NOT EXISTS 'FINISHED';

-- 2. Migrate existing data
-- Move 'SCHEDULED' to 'NOT_YET_OPEN' as a safe default.
-- The cron job will look at time and move them to the correct state shortly after.
UPDATE events SET status = 'NOT_YET_OPEN' WHERE status = 'SCHEDULED';

-- 3. 'SCHEDULED' is now deprecated. We keep it in the enum for now to avoid complex type migration,
-- but we ensure no rows use it.
