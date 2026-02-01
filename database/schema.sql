-- Enum types
CREATE TYPE event_status AS ENUM ('SCHEDULED', 'CANCELLED');
CREATE TYPE list_type AS ENUM ('EVENT', 'WAITLIST', 'WAITLIST_HOLDING');

-- User Groups
CREATE TABLE user_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE
);

-- Profiles (Public user data linked to auth.users)
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT,
  email TEXT,
  user_group_id UUID REFERENCES user_groups(id)
);

-- Turn on Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_groups ENABLE ROW LEVEL SECURITY;

-- Events
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  status event_status DEFAULT 'SCHEDULED',
  max_signups INTEGER NOT NULL DEFAULT 10,
  event_date TIMESTAMP WITH TIME ZONE NOT NULL,
  roster_sign_up_open TIMESTAMP WITH TIME ZONE NOT NULL,
  waitlist_sign_up_open TIMESTAMP WITH TIME ZONE NOT NULL,
  reserve_sign_up_open TIMESTAMP WITH TIME ZONE NOT NULL,
  initial_reserve_scheduling TIMESTAMP WITH TIME ZONE NOT NULL,
  final_reserve_scheduling TIMESTAMP WITH TIME ZONE NOT NULL
);

ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Event Signups (The lists)
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

-- Policies (Simple open policies for now, refine later)
CREATE POLICY "Public profiles are viewable by everyone" ON profiles FOR SELECT USING (true);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "User groups are viewable by everyone" ON user_groups FOR SELECT USING (true);

CREATE POLICY "Events are viewable by everyone" ON events FOR SELECT USING (true);

CREATE POLICY "Signups are viewable by everyone" ON event_signups FOR SELECT USING (true);
CREATE POLICY "Users can insert their own signup" ON event_signups FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own signup" ON event_signups FOR DELETE USING (auth.uid() = user_id);
