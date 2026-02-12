-- Migration: Standardize User Group Names
-- Date: 2026-02-12
-- Goal: Rename "SecondaryPriority" -> "SecondPriority", "Primary" -> "FirstPriority", etc.

DO $$
DECLARE
    first_priority_id UUID;
    second_priority_id UUID;
    old_id UUID;
BEGIN
    -- 1. Ensure Standard Groups Exist
    INSERT INTO user_groups (name, description) 
    VALUES ('FirstPriority', 'Standardized First Priority Group') 
    ON CONFLICT (name) DO NOTHING;
    
    INSERT INTO user_groups (name, description) 
    VALUES ('SecondPriority', 'Standardized Second Priority Group') 
    ON CONFLICT (name) DO NOTHING;

    -- Get Standard IDs
    SELECT id INTO first_priority_id FROM user_groups WHERE name = 'FirstPriority';
    SELECT id INTO second_priority_id FROM user_groups WHERE name = 'SecondPriority';

    RAISE NOTICE 'Standard IDs: First=%, Second=%', first_priority_id, second_priority_id;

    -- 2. Merge "SecondaryPriority" -> "SecondPriority"
    SELECT id INTO old_id FROM user_groups WHERE name = 'SecondaryPriority';
    IF old_id IS NOT NULL AND old_id != second_priority_id THEN
        RAISE NOTICE 'Merging SecondaryPriority (%) into SecondPriority', old_id;
        -- Update referencing tables? profile_groups is the main one.
        -- We use ON CONFLICT DO NOTHING to avoid duplicate (user, group) pairs if they are already in both.
        UPDATE profile_groups SET group_id = second_priority_id WHERE group_id = old_id 
        ON CONFLICT (profile_id, group_id) DO NOTHING;
        
        -- Delete remaining (those that were conflicts)
        DELETE FROM profile_groups WHERE group_id = old_id;
        
        -- Update Event Types (if they pointed to old group)
        UPDATE event_types SET reserve_second_priority_user_group = second_priority_id WHERE reserve_second_priority_user_group = old_id;
        
        DELETE FROM user_groups WHERE id = old_id;
    END IF;

    -- 3. Merge "Secondary" -> "SecondPriority"
    SELECT id INTO old_id FROM user_groups WHERE name = 'Secondary';
    IF old_id IS NOT NULL AND old_id != second_priority_id THEN
        RAISE NOTICE 'Merging Secondary (%) into SecondPriority', old_id;
        UPDATE profile_groups SET group_id = second_priority_id WHERE group_id = old_id 
        ON CONFLICT (profile_id, group_id) DO NOTHING;
        DELETE FROM profile_groups WHERE group_id = old_id;
        DELETE FROM user_groups WHERE id = old_id;
    END IF;

    -- 4. Merge "Primary" -> "FirstPriority"
    SELECT id INTO old_id FROM user_groups WHERE name = 'Primary';
    IF old_id IS NOT NULL AND old_id != first_priority_id THEN
        RAISE NOTICE 'Merging Primary (%) into FirstPriority', old_id;
        UPDATE profile_groups SET group_id = first_priority_id WHERE group_id = old_id 
        ON CONFLICT (profile_id, group_id) DO NOTHING;
        DELETE FROM profile_groups WHERE group_id = old_id;
        UPDATE event_types SET reserve_first_priority_user_group = first_priority_id WHERE reserve_first_priority_user_group = old_id;
        DELETE FROM user_groups WHERE id = old_id;
    END IF;

    -- 5. Explicitly Update Event Types to ensure they behave
    -- (Just in case they were pointing to something else or NULL)
    UPDATE event_types 
    SET reserve_first_priority_user_group = first_priority_id
    WHERE reserve_first_priority_user_group IS NULL OR reserve_first_priority_user_group != first_priority_id;

    UPDATE event_types 
    SET reserve_second_priority_user_group = second_priority_id
    WHERE reserve_second_priority_user_group IS NULL OR reserve_second_priority_user_group != second_priority_id;

END $$;
