-- Insert User Groups
-- We use ON CONFLICT DO NOTHING to avoid duplicates if running multiple times (though simple script might error without constraint on name if not unique, schema says unique)
INSERT INTO user_groups (name, description)
VALUES 
  ('SuperAdmin', 'Has full unrestricted access to all parts of the system.'),
  ('Admin', 'Initially has the same access as SuperAdmin, but this may change in the future.'),
  ('FirstPriority', 'Used by certain system functionality to determine order among users (e.g., scheduling) — grants first priority.'),
  ('SecondPriority', 'Used by certain system functionality to determine order among users — grants second priority.'),
  ('BethAmAffiliated', 'Notes those users who have an affiliation with Beth Am.'),
  
  -- New Groups
  ('SundayBasketball', 'Roster for Sunday games'),
  ('TuesdayBasketball', 'Roster for Tuesday games'),
  ('ThursdayBasketball', 'Roster for Thursday games'),
  ('SundayBasketballReserves', 'Reserves for Sunday games'),
  ('TuesdayBasketballReserves', 'Reserves for Tuesday games'),
  ('ThursdayBasketballReserves', 'Reserves for Thursday games')
ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description;

-- Insert Event Type (Tuesday Basketball)
-- We need to capture the ID to use it for the event
DO $$
DECLARE
    tuesday_type_id UUID;
    roster_group_id UUID;
    reserve_1_group_id UUID;
    reserve_2_group_id UUID;
BEGIN
    -- Get Group IDs
    SELECT id INTO roster_group_id FROM user_groups WHERE name = 'TuesdayBasketball';
    SELECT id INTO reserve_1_group_id FROM user_groups WHERE name = 'FirstPriority';
    SELECT id INTO reserve_2_group_id FROM user_groups WHERE name = 'SecondPriority';

    -- Insert Event Type
    INSERT INTO event_types (
        name,
        day_of_week,
        time_of_day,
        max_signups,
        roster_user_group,
        reserve_first_priority_user_group,
        reserve_second_priority_user_group,
        duration
    ) VALUES (
        'Tuesday Night Basketball',
        2, -- Tuesday
        '20:00:00',
        15,
        roster_group_id,
        reserve_1_group_id,
        reserve_2_group_id,
        '90 minutes' -- Specific duration for this type
    )
    ON CONFLICT DO NOTHING -- Only if we had a unique constraint on name, passing for now
    RETURNING id INTO tuesday_type_id;

    -- If we didn't insert (because it exists), try to fetch it? 
    -- For simplicity in seed, we assume clean slate or just insert.
    -- If variable is null, let's look it up
    IF tuesday_type_id IS NULL THEN
        SELECT id INTO tuesday_type_id FROM event_types WHERE name = 'Tuesday Night Basketball' LIMIT 1;
    END IF;

    -- Insert Event (Next Tuesday)
    -- Calculate next Tuesday
    -- For seed simplicity, just create one for 7 days from now
    IF tuesday_type_id IS NOT NULL THEN
        INSERT INTO events (
            event_type_id,
            event_date,
            status,
            status_determinant
        ) VALUES (
            tuesday_type_id,
            NOW() + INTERVAL '7 days',
            'NOT_YET_OPEN',
            'AUTOMATIC'
        );
    END IF;
END $$;
