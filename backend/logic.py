import random
from datetime import datetime, timedelta, timezone

def enrich_event(event_data, now=None):
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

    # Calculate/Confirm Status
    # In the new architecture, the Database is the Single Source of Truth for Status.
    # The Cron Job updates it.
    # HOWEVER: For backward compatibility during migration tailored to user request:
    # If status is "SCHEDULED" (deprecated), calculate it dynamically.
    # If status is one of the new valid ones, USE IT AS IS.
    
    current_status = event_data.get("status")
    
    if current_status == "SCHEDULED":
        if now is None:
            now = datetime.now(timezone.utc)
        event_data["status"] = determine_event_status(event_data, now)
    
    # Otherwise, trust the DB (e.g. NOT_YET_OPEN, OPEN_FOR_ROSTER, etc.)
    # This ensures consistency between API and direct DB reads.

    return event_data


def determine_event_status(event, now):
    """
    Calculates the correct EventStatus based on time windows.
    Does NOT handle 'CANCELLED' as that is a manual override.
    
    Args:
        event (dict): Enriched event object
        now (datetime): Current timestamp
    
    Returns:
        str: one of EventStatus values
    """
    # Parse times
    def to_dt(val):
        if not val: return None
        if isinstance(val, datetime): return val
        return datetime.fromisoformat(str(val).replace('Z', '+00:00'))

    # If already cancelled, stay cancelled (this function is usually for auto-updates)
    # But usually the caller handles the "if not cancelled" check. 
    # We will return the TIME-BASED status here.
    
    roster_open = to_dt(event.get("roster_sign_up_open"))
    reserve_open = to_dt(event.get("reserve_sign_up_open"))
    initial_scheduling = to_dt(event.get("initial_reserve_scheduling"))
    final_scheduling = to_dt(event.get("final_reserve_scheduling"))
    
    # Assuming event_date is start time
    event_start = to_dt(event.get("event_date"))
    
    if now < roster_open:
        return "NOT_YET_OPEN"
    elif now < reserve_open:
        return "OPEN_FOR_ROSTER"
    elif now < initial_scheduling:
        return "OPEN_FOR_RESERVES"
    elif now < final_scheduling:
        return "PRELIMINARY_ORDERING"
    elif now < event_start:
        return "FINAL_ORDERING"
    else:
        return "FINISHED"

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
    status = event.get("status")

    # determine efficient status
    # If legacy 'SCHEDULED', calculate it on the fly
    if status == "SCHEDULED":
        status = determine_event_status(event, now)

    # 0. Strict Status Enforcement
    if status == "CANCELLED":
        return {"allowed": False, "error_message": "Event is cancelled."}
    if status == "FINISHED":
        return {"allowed": False, "error_message": "Event has finished."}
    if status == "NOT_YET_OPEN":
        return {"allowed": False, "error_message": "Event signups are not yet open."}
        
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

    # 2. Status-Based Logic
    
    # OPEN_FOR_ROSTER: Roster only -> EVENT/WAITLIST
    if status == "OPEN_FOR_ROSTER":
        if tier == 1:
            return {"allowed": True, "tier": 1, "target_list": "EVENT"}
        else:
             # Even if Roster is full, reserves cannot sign up yet.
             return {"allowed": False, "error_message": "Event is currently open for Roster members only."}

    # OPEN_FOR_RESERVES / PRELIMINARY_ORDERING:
    # Roster -> EVENT/WAITLIST
    # Reserves -> HOLDING
    if status in ["OPEN_FOR_RESERVES", "PRELIMINARY_ORDERING"]:
        if tier == 1:
             return {"allowed": True, "tier": tier, "target_list": "EVENT"}
        else: # Tier 2 or 3
             return {"allowed": True, "tier": tier, "target_list": "WAITLIST_HOLDING"}

    # FINAL_ORDERING:
    # Everyone -> EVENT/WAITLIST
    if status == "FINAL_ORDERING":
        return {"allowed": True, "tier": tier, "target_list": "EVENT"}
             
    return {"allowed": False, "error_message": f"Unknown event status: {status}"}

def randomize_holding_queue(holding_users):
    """
    Randomizes a list of holding_users based on Tier logic:
    - Group by Tier
    - Randomize Tier 2
    - Randomize Tier 3
    - Return Tier 2 + Tier 3
    
    Returns:
        list: Sorted list of users (dicts)
    """
    if not holding_users:
        return []
            
    # Group by Tier
    # Assuming 'tier' is present in user dict
    tier2 = [u for u in holding_users if u.get("tier") == 2]
    tier3 = [u for u in holding_users if u.get("tier") == 3]
    others = [u for u in holding_users if u.get("tier") not in [2, 3]]
    
    # Randomize
    random.shuffle(tier2)
    random.shuffle(tier3)
    # Others? Maybe append at end
    
    return tier2 + tier3 + others

def promote_from_holding(queue, current_roster_count, max_signups, current_waitlist_count):
    """
    takes an ALREADY SORTED queue and assigns them to EVENT or WAITLIST.
    
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
            "user_id": user.get('user_id'),
            "list_type": new_list,
            "sequence_number": new_seq
        })
        
    return updates


def resequence_holding(queue):
    """
    Takes a randomized queue of users and assigns them new sequence numbers
    keeping them in WAITLIST_HOLDING.
    
    Returns a list of dicts:
    [
        {"id": user_id, "list_type": "WAITLIST_HOLDING", "sequence_number": 1},
        ...
    ]
    """
    updates = []
    for i, user in enumerate(queue):
        updates.append({
            "id": user['id'],
            "user_id": user.get('user_id'),
            "list_type": "WAITLIST_HOLDING",
            "sequence_number": i + 1
        })
    return updates
