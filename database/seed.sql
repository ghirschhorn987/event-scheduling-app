
-- Insert User Group
INSERT INTO user_groups (name)
VALUES ('Basketball Regulars')
ON CONFLICT (name) DO NOTHING;

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
