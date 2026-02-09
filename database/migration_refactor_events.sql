-- Migration: Split Events into Classes and Instances

DROP TABLE IF EXISTS event_signups;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS event_types CASCADE;
DROP TABLE IF EXISTS event_templates CASCADE;
DROP TABLE IF EXISTS event_classes CASCADE; -- Cleanup old if exists

-- Re-create tables
CREATE TABLE event_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  day_of_week INTEGER NOT NULL, -- 0=Sunday, 6=Saturday
  time_of_day TIME NOT NULL,
  time_zone TEXT NOT NULL DEFAULT 'America/Los_Angeles',
  max_signups INTEGER NOT NULL DEFAULT 15,
  roster_sign_up_open_minutes INTEGER NOT NULL DEFAULT 4320, -- 3 days
  reserve_sign_up_open_minutes INTEGER NOT NULL DEFAULT 720, -- 12 hours
  initial_reserve_scheduling_minutes INTEGER NOT NULL DEFAULT 420, -- 7 hours
  final_reserve_scheduling_minutes INTEGER NOT NULL DEFAULT 180 -- 3 hours
);

ALTER TABLE event_types ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Event Types are viewable by everyone" ON event_types FOR SELECT USING (true);


CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type_id UUID REFERENCES event_types(id) ON DELETE CASCADE,
  event_date TIMESTAMP WITH TIME ZONE NOT NULL,
  status event_status DEFAULT 'SCHEDULED'
);

ALTER TABLE events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Events are viewable by everyone" ON events FOR SELECT USING (true);

-- Re-create Signups
CREATE TABLE event_signups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID REFERENCES events(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  list_type list_type NOT NULL,
  sequence_number INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  UNIQUE(event_id, user_id)
);

ALTER TABLE event_signups ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Signups are viewable by everyone" ON event_signups FOR SELECT USING (true);
CREATE POLICY "Users can insert their own signup" ON event_signups FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own signup" ON event_signups FOR DELETE USING (auth.uid() = user_id);
