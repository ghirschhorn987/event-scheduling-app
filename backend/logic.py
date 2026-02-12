import random
from datetime import datetime, timedelta

def enrich_event(event_data):
    """
    Takes raw event data (joined with event_types) and computes the detailed timestamps
    and fields expected by the frontend 'Event' model.
    """
    # Prefer event_types, fallback to event_classes just in case legacy code passes it
    event_type = event_data.get("event_types") or event_data.get("event_classes")
    
    if not event_type:
        # Should not happen if FK is enforced and query is correct
        return event_data

    # Handle both string (ISO) and datetime objects for robustness in tests
    if isinstance(event_data["event_date"], str):
        event_date = datetime.fromisoformat(event_data["event_date"].replace('Z', '+00:00'))
    else:
        event_date = event_data["event_date"]
    
    # Enrich fields
    event_data["name"] = event_type["name"]
    event_data["max_signups"] = event_type["max_signups"]
    
    # Group permissions
    event_data["roster_user_group"] = event_type.get("roster_user_group")
    event_data["reserve_first_priority_user_group"] = event_type.get("reserve_first_priority_user_group")
    event_data["reserve_second_priority_user_group"] = event_type.get("reserve_second_priority_user_group")
    
    # Calculate timestamps
    # Timedeltas in minutes
    event_data["roster_sign_up_open"] = event_date - timedelta(minutes=event_type["roster_sign_up_open_minutes"])
    event_data["reserve_sign_up_open"] = event_date - timedelta(minutes=event_type["reserve_sign_up_open_minutes"])
    
    event_data["initial_reserve_scheduling"] = event_date - timedelta(minutes=event_type["initial_reserve_scheduling_minutes"])
    event_data["final_reserve_scheduling"] = event_date - timedelta(minutes=event_type["final_reserve_scheduling_minutes"])
    
    event_data["waitlist_sign_up_open"] = event_data["roster_sign_up_open"]

    return event_data


def check_signup_eligibility(event, user_groups, now):
    """
    Determines if a user can sign up for an event and which list they should join.
    
    Args:
        event (dict): Enriched event object
        user_groups (list): List of group names or IDs the user belongs to
        now (datetime): Current timestamp
        
    Returns:
        dict: {
            "allowed": bool,
            "tier": int (1, 2, or 3),
            "target_list": str ("EVENT", "WAITLIST", "WAITLIST_HOLDING"),
            "error_message": str (optional)
        }
    """
    # 1. Determine Tier
    tier = None
    
    # Check Tier 1 (Roster)
    if event.get("roster_user_group") and event["roster_user_group"] in user_groups:
        tier = 1
    # Check Tier 2 (First Priority)
    elif event.get("reserve_first_priority_user_group") and event["reserve_first_priority_user_group"] in user_groups:
        tier = 2
    # Check Tier 3 (Second Priority)
    elif event.get("reserve_second_priority_user_group") and event["reserve_second_priority_user_group"] in user_groups:
        tier = 3
        
    if not tier:
        return {"allowed": False, "error_message": "No valid membership for this event"}

    # 2. Check Windows based on Tier
    
    # Parse times if strings
    def to_dt(val):
        if not val: return None
        if isinstance(val, datetime): return val
        return datetime.fromisoformat(str(val).replace('Z', '+00:00'))

    roster_open = to_dt(event.get("roster_sign_up_open"))
    reserve_open = to_dt(event.get("reserve_sign_up_open"))
    final_scheduling = to_dt(event.get("final_reserve_scheduling"))
    
    # Tier 1 Logic
    if tier == 1:
        if now >= roster_open:
            return {"allowed": True, "tier": 1, "target_list": "EVENT"}
        else:
            return {"allowed": False, "error_message": f"Not yet open for Roster members. Opens at {roster_open}"}
            
    # Tier 2 & 3 Logic
    if tier in [2, 3]:
        # If Reserve window hasn't opened yet
        if now < reserve_open:
             return {"allowed": False, "error_message": f"Not yet open for Reserve members. Opens at {reserve_open}"}
        
        # If inside Reserve Window but BEFORE Final Scheduling -> HOLDING
        if now < final_scheduling:
            return {"allowed": True, "tier": tier, "target_list": "WAITLIST_HOLDING"}
            
        # If AFTER Final Scheduling -> Direct Entry (First come first serve)
        else:
             return {"allowed": True, "tier": tier, "target_list": "EVENT"}
             
    return {"allowed": False, "error_message": "Unknown error"}

def process_holding_queue(holding_users, initial_reserve_scheduling_time):
    """
    Sorts a list of holding_users based on the hybrid logic:
    - Early (created_at < initial_scheduling):
        - Tier 2 Randomized
        - Tier 3 Randomized
        - Tier 2 + Tier 3
    - Late (created_at >= initial_scheduling):
        - Sorted by created_at
        
    Args:
        holding_users (list): List of user dicts, must include 'tier' and 'created_at'
        initial_reserve_scheduling_time (datetime): The cutoff time
    
    Returns:
        list: Sorted list of users
    """
    if not holding_users:
        return []
        
    def to_dt(val):
        if not val: return datetime.min
        if isinstance(val, datetime): return val
        return datetime.fromisoformat(str(val).replace('Z', '+00:00'))
    
    initial_time = to_dt(initial_reserve_scheduling_time)

    early = []
    late = []
    
    for u in holding_users:
        created_at = to_dt(u.get("created_at"))
        if created_at < initial_time:
            early.append(u)
        else:
            late.append(u)
            
    # Sort Early
    # Group by Tier
    early_t2 = [u for u in early if u.get("tier") == 2]
    early_t3 = [u for u in early if u.get("tier") == 3] # Or anything else
    
    # Randomize
    random.shuffle(early_t2)
    random.shuffle(early_t3)
    
    # Sort Late by time
    late.sort(key=lambda x: to_dt(x.get("created_at")))
    
    return early_t2 + early_t3 + late

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
