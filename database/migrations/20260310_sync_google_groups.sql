-- 1. Drop redundant column
ALTER TABLE user_groups DROP COLUMN IF EXISTS google_group_id;

-- 2. Insert new groups (Assuming names don't exist)
INSERT INTO user_groups (name, description, guest_limit, group_type, group_email) VALUES
('BethAmHoopsSundayRoster', 'Sunday Roster - Paid priority players', 2, 'EVENT_ELIGIBILITY', 'beth-am-hoops-sunday-roster@skeddle.net'),
('BethAmHoopsSundayReserves', 'Sunday Reserves', 0, 'EVENT_ELIGIBILITY', 'beth-am-hoops-sunday-reserves@skeddle.net'),
('BethAmHoopsTuesdayRoster', 'Tuesday Roster - Paid priority players', 2, 'EVENT_ELIGIBILITY', 'beth-am-hoops-tuesday-roster@skeddle.net'),
('BethAmHoopsTuesdayReserves', 'Tuesday Reserves', 0, 'EVENT_ELIGIBILITY', 'beth-am-hoops-tuesday-reserves@skeddle.net'),
('BethAmHoopsThursdayRoster', 'Thursday Roster - Paid priority players', 2, 'EVENT_ELIGIBILITY', 'beth-am-hoops-thursday-roster@skeddle.net'),
('BethAmHoopsThursdayReserves', 'Thursday Reserves', 0, 'EVENT_ELIGIBILITY', 'beth-am-hoops-thursday-reserves@skeddle.net')
ON CONFLICT DO NOTHING;
