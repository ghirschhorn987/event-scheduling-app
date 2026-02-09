import random
from datetime import datetime, timedelta

def enrich_event(event_data):
    """
    Takes raw event data (joined with event_classes) and computes the detailed timestamps
    and fields expected by the frontend 'Event' model.
    """
    event_class = event_data.get("event_classes")
    if not event_class:
        # Should not happen if FK is enforced
        return event_data

    # Handle both string (ISO) and datetime objects for robustness in tests
    if isinstance(event_data["event_date"], str):
        event_date = datetime.fromisoformat(event_data["event_date"].replace('Z', '+00:00'))
    else:
        event_date = event_data["event_date"]
    
    # Enrich fields
    event_data["name"] = event_class["name"]
    event_data["max_signups"] = event_class["max_signups"]
    
    # Calculate timestamps
    # Timedeltas in minutes
    event_data["roster_sign_up_open"] = event_date - timedelta(minutes=event_class["roster_sign_up_open_minutes"])
    event_data["reserve_sign_up_open"] = event_date - timedelta(minutes=event_class["reserve_sign_up_open_minutes"])
    
    event_data["initial_reserve_scheduling"] = event_date - timedelta(minutes=event_class["initial_reserve_scheduling_minutes"])
    event_data["final_reserve_scheduling"] = event_date - timedelta(minutes=event_class["final_reserve_scheduling_minutes"])
    
    event_data["waitlist_sign_up_open"] = event_data["roster_sign_up_open"]

    return event_data

def process_holding_queue(holding_users):
    """
    Sorts a list of holding_users based on the hybrid logic:
    - Window 1 (seq -1 key missing): Random Shuffle
    - Window 2 (seq > 0): Sorted by sequence
    
    Returns a single ordered list of users to promote.
    """
    if not holding_users:
        return []

    window1 = [u for u in holding_users if not u.get('sequence_number') or u.get('sequence_number') < 0]
    window2 = [u for u in holding_users if u.get('sequence_number') and u.get('sequence_number') > 0]
    
    # Shuffle Window 1
    # We use a fixed seed for deterministic testing if needed, but here random is fine?
    # For Unit Tests, we might want to mock random.shuffle.
    random.shuffle(window1)
    
    # Sort Window 2
    window2.sort(key=lambda x: x['sequence_number'])
    
    return window1 + window2

def calculate_promotions(queue, current_roster_count, max_signups, current_waitlist_count):
    """
    Calculates the new status for each user in the queue.
    Returns a list of dicts:
    [
        {"id": user_id, "list_type": "EVENT", "sequence_number": 1},
        ...
    ]
    """
    updates = []
    local_roster_count = current_roster_count
    local_waitlist_count = current_waitlist_count
    
    for user in queue:
        signup_id = user['id']
        new_list = "EVENT"
        new_seq = 0
        
        if local_roster_count < max_signups:
            new_list = "EVENT"
            local_roster_count += 1
            new_seq = local_roster_count
        else:
            new_list = "WAITLIST"
            local_waitlist_count += 1
            new_seq = local_waitlist_count
            
        updates.append({
            "id": signup_id,
            "list_type": new_list,
            "sequence_number": new_seq
        })
        
    return updates
