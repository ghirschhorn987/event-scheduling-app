-- Move duration from events to event_types

-- 1. Add duration column to event_types with default 120 minutes
ALTER TABLE event_types ADD COLUMN duration INTERVAL NOT NULL DEFAULT '120 minutes';

-- 2. Drop duration column from events
ALTER TABLE events DROP COLUMN IF EXISTS duration;

-- Optional: Comment
COMMENT ON COLUMN event_types.duration IS 'Duration of the event type, used to calculate FINISHED status.';
