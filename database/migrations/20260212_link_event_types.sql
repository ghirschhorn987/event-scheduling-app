-- 1. Ensure User Groups Exist
INSERT INTO user_groups (name, description)
VALUES 
  ('FirstPriority', 'Used by certain system functionality to determine order among users (e.g., scheduling) — grants first priority.'),
  ('SecondPriority', 'Used by certain system functionality to determine order among users — grants second priority.')
ON CONFLICT (name) DO NOTHING;

-- 2. Update Event Types to point to these groups

-- Sunday Basketball
UPDATE event_types
SET 
  roster_user_group = (SELECT id FROM user_groups WHERE name = 'SundayBasketball'),
  reserve_first_priority_user_group = (SELECT id FROM user_groups WHERE name = 'FirstPriority'),
  reserve_second_priority_user_group = (SELECT id FROM user_groups WHERE name = 'SecondPriority')
WHERE name = 'Sunday Basketball';

-- Tuesday Basketball
UPDATE event_types
SET 
  roster_user_group = (SELECT id FROM user_groups WHERE name = 'TuesdayBasketball'),
  reserve_first_priority_user_group = (SELECT id FROM user_groups WHERE name = 'FirstPriority'),
  reserve_second_priority_user_group = (SELECT id FROM user_groups WHERE name = 'SecondPriority')
WHERE name = 'Tuesday Basketball';

-- Thursday Basketball
UPDATE event_types
SET 
  roster_user_group = (SELECT id FROM user_groups WHERE name = 'ThursdayBasketball'),
  reserve_first_priority_user_group = (SELECT id FROM user_groups WHERE name = 'FirstPriority'),
  reserve_second_priority_user_group = (SELECT id FROM user_groups WHERE name = 'SecondPriority')
WHERE name = 'Thursday Basketball';
