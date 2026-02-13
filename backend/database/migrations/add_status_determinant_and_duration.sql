-- Add event_status_determinant enum and duration field

-- 1. Create Enum
CREATE TYPE event_status_determinant AS ENUM ('AUTOMATIC', 'MANUAL');

-- 2. Add columns to events table
ALTER TABLE events 
ADD COLUMN status_determinant event_status_determinant NOT NULL DEFAULT 'AUTOMATIC',
ADD COLUMN duration INTERVAL;

-- Optional: Comment describing the new fields
COMMENT ON COLUMN events.status_determinant IS 'Determines if status is updated automatically by cron (AUTOMATIC) or manually by admin (MANUAL)';
COMMENT ON COLUMN events.duration IS 'Duration of the event';
