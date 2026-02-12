-- Insert User Groups
INSERT INTO user_groups (name, description)
VALUES 
  ('SuperAdmin', 'Has full unrestricted access to all parts of the system.'),
  ('Admin', 'Initially has the same access as SuperAdmin, but this may change in the future.'),
  ('FirstPriority', 'Used by certain system functionality to determine order among users (e.g., scheduling) — grants first priority.'),
  ('SecondaryPriority', 'Used by certain system functionality to determine order among users — grants second priority.'),
  ('BethAmAffiliated', 'Notes those users who have an affiliation with Beth Am.'),
  ('FirstPriority', 'Used by certain system functionality to determine order among users (e.g., scheduling) — grants first priority.'),
  ('SecondPriority', 'Used by certain system functionality to determine order among users — grants second priority.'),
  ('SundayBasketball', 'contains paid roster of Sunday players'),
  ('TuesdayBasketball', 'contains paid roster of Tuesday players'),
  ('ThursdayBasketball', 'contains paid roster of Thursday players')
ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description;

-- Insert Event
INSERT INTO events (
  name, 
  max_signups, 
  event_date, 
  roster_sign_up_open, 
  waitlist_sign_up_open, 
  reserve_sign_up_open, 
  initial_reserve_scheduling, 
  final_reserve_scheduling
)
VALUES (
  'Weekly Basketball',
  15,
  NOW() + INTERVAL '7 days',                -- Event in 7 days
  NOW() + INTERVAL '1 day',                 -- Roster open in 1 day
  NOW() + INTERVAL '2 days',                -- Waitlist open in 2 days
  NOW() + INTERVAL '3 days',                -- Reserve open in 3 days
  NOW() + INTERVAL '5 days',                -- Initial scheduling in 5 days
  NOW() + INTERVAL '6 days'                 -- Final scheduling in 6 days
);
