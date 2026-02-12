-- Add group restriction fields to event_types
ALTER TABLE event_types
ADD COLUMN roster_user_group UUID REFERENCES user_groups(id),
ADD COLUMN reserve_first_priority_user_group UUID REFERENCES user_groups(id),
ADD COLUMN reserve_second_priority_user_group UUID REFERENCES user_groups(id);

-- Commentary: These fields allow restricting who can sign up for specific slots.
-- roster_user_group: Users in this group can sign up during the primary roster window.
-- reserve_first_priority_user_group: Users in this group get priority in the holding area.
-- reserve_second_priority_user_group: Users in this group get secondary priority.
