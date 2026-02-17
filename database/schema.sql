-- Enum types
CREATE TYPE event_status AS ENUM ('SCHEDULED', 'CANCELLED', 'NOT_YET_OPEN', 'OPEN_FOR_ROSTER', 'OPEN_FOR_RESERVES', 'PRELIMINARY_ORDERING', 'FINAL_ORDERING', 'FINISHED');
CREATE TYPE list_type AS ENUM ('EVENT', 'WAITLIST', 'WAITLIST_HOLDING');
CREATE TYPE event_status_determinant AS ENUM ('AUTOMATIC', 'MANUAL');

-- User Groups
CREATE TABLE user_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  google_group_id TEXT
);

-- Profiles (Public user data linked to auth.users)
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  auth_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT
);

CREATE TABLE profile_groups (
  profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  group_id UUID REFERENCES user_groups(id) ON DELETE CASCADE,
  PRIMARY KEY (profile_id, group_id)
);

-- Turn on Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_groups ENABLE ROW LEVEL SECURITY;

-- Canceled Dates (Blocklist)
CREATE TABLE cancelled_dates (
    date DATE PRIMARY KEY,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
ALTER TABLE cancelled_dates ENABLE ROW LEVEL SECURITY;

-- Events
-- Event Types (Definitions for recurring events)
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
  final_reserve_scheduling_minutes INTEGER NOT NULL DEFAULT 180, -- 3 hours
  roster_user_group UUID REFERENCES user_groups(id),
  reserve_first_priority_user_group UUID REFERENCES user_groups(id),
  reserve_second_priority_user_group UUID REFERENCES user_groups(id),
  duration INTERVAL NOT NULL DEFAULT '120 minutes'
);

ALTER TABLE event_types ENABLE ROW LEVEL SECURITY;

-- Events (Instances)
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type_id UUID REFERENCES event_types(id) ON DELETE CASCADE,
  event_date TIMESTAMP WITH TIME ZONE NOT NULL,
  status event_status DEFAULT 'NOT_YET_OPEN',
  status_determinant event_status_determinant NOT NULL DEFAULT 'AUTOMATIC'
);

ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Event Signups (The lists)
CREATE TABLE event_signups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id UUID REFERENCES events(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  list_type list_type NOT NULL,
  sequence_number INTEGER,
  tier INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  UNIQUE(event_id, user_id)
);

ALTER TABLE event_signups ENABLE ROW LEVEL SECURITY;

-- Registration Requests (New user queue)
CREATE TABLE registration_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    affiliation TEXT NOT NULL,
    referral TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, APPROVED, DECLINED, INFO_NEEDED
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
ALTER TABLE registration_requests ENABLE ROW LEVEL SECURITY;


-- Policies (Simple open policies for now, refine later)
CREATE POLICY "Public profiles are viewable by everyone" ON profiles FOR SELECT USING (true);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "User groups are viewable by everyone" ON user_groups FOR SELECT USING (true);
CREATE POLICY "Profile groups are viewable by everyone" ON profile_groups FOR SELECT USING (true);

CREATE POLICY "Events are viewable by everyone" ON events FOR SELECT USING (true);
CREATE POLICY "Event types are viewable by everyone" ON event_types FOR SELECT USING (true);
CREATE POLICY "Cancelled dates are viewable by authenticated" ON cancelled_dates FOR SELECT TO authenticated USING (true);

CREATE POLICY "Signups are viewable by everyone" ON event_signups FOR SELECT USING (true);
CREATE POLICY "Users can insert their own signup" ON event_signups FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete their own signup" ON event_signups FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Registration requests viewable by everyone" ON registration_requests FOR SELECT USING (true);
CREATE POLICY "Public insert registration" ON registration_requests FOR INSERT WITH CHECK (true);
