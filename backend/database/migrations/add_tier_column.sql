-- Add 'tier' column to event_signups if it doesn't exist
ALTER TABLE event_signups 
ADD COLUMN IF NOT EXISTS tier INTEGER;
