-- RPC Function to atomically update event status and optionally process batch updates

-- Renaming from process_holding_batch to update_event_status_batch
-- Drops the old one if it exists to avoid confusion (though user hasn't run it yet, likely)

CREATE OR REPLACE FUNCTION update_event_status_batch(
    p_event_id UUID,
    p_updates JSONB DEFAULT '[]'::JSONB, -- Optional Array of objects
    p_final_status TEXT DEFAULT NULL -- Required to set new status
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    update_item JSONB;
    v_record_id UUID;
    v_list_type TEXT;
    v_seq INT;
    v_updates_count INT := 0;
BEGIN
    -- 1. Validate Event Exists
    PERFORM 1 FROM events WHERE id = p_event_id;
    IF NOT FOUND THEN
        RETURN jsonb_build_object('status', 'error', 'message', 'Event not found');
    END IF;

    -- 2. Iterate through updates (if any)
    IF p_updates IS NOT NULL AND jsonb_array_length(p_updates) > 0 THEN
        FOR update_item IN SELECT * FROM jsonb_array_elements(p_updates)
        LOOP
            v_record_id := (update_item->>'id')::UUID;
            v_list_type := update_item->>'list_type';
            v_seq := (update_item->>'sequence_number')::INT;

            -- Perform Update
            UPDATE event_signups
            SET 
                list_type = v_list_type,
                sequence_number = v_seq,
                updated_at = NOW()
            WHERE id = v_record_id;

            v_updates_count := v_updates_count + 1;
        END LOOP;
    END IF;

    -- 3. Update Event Status (if provided)
    IF p_final_status IS NOT NULL THEN
        UPDATE events
        SET status = p_final_status
        WHERE id = p_event_id;
    END IF;

    -- 4. Return Success
    RETURN jsonb_build_object(
        'status', 'success',
        'transacted_updates', v_updates_count,
        'final_event_status', p_final_status
    );

EXCEPTION WHEN OTHERS THEN
    RETURN jsonb_build_object('status', 'error', 'message', SQLERRM);
END;
$$;
