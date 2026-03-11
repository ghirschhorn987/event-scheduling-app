import pytest
import sys
import os
from datetime import datetime, timedelta, timezone

# Add parent directory to path to import logic
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import check_signup_eligibility, randomize_holding_queue

# Mock Event Data
def get_mock_event(now_dt):
    """
    Creates a mock event with windows relative to 'now_dt'.
    Event starts in 24 hours.
    Roster Open: 4 hours before start (20 hours from now)
    Reserve Open: 24 hours before start (NOW)
    Initial Reserve Scheduling: 12 hours before start (12 hours from now)
    Final Reserve Scheduling: 2 hours before start (22 hours from now)
    """
    event_start = now_dt + timedelta(hours=24)
    return {
        "id": "evt1",
        "name": "Test Event",
        "max_signups": 10,
        "roster_user_group": "group_roster",
        "reserve_first_priority_user_group": "group_p1",
        "reserve_second_priority_user_group": "group_p2",
        "roster_sign_up_open": event_start - timedelta(hours=4),
        "reserve_sign_up_open": event_start - timedelta(hours=24), # Open NOW
        "initial_reserve_scheduling": event_start - timedelta(hours=12),
        "final_reserve_scheduling": event_start - timedelta(hours=2),
    }

def test_signup_eligibility_tier1_early():
    # Tier 1 user, before roster window -> Denied
    now = datetime(2026, 2, 10, 10, 0, 0, tzinfo=timezone.utc)
    event = get_mock_event(now) # Reserve opens now, Roster opens in 20h
    
    user_groups = ["group_roster"]
    
    # We need to set a valid status to trigger the check instead of 'Unknown' fallback
    event["status"] = "NOT_YET_OPEN"
    
    result = check_signup_eligibility(event, user_groups, now)
    assert result["allowed"] == False
    assert "Event signups are not yet open" in result["error_message"]

def test_signup_eligibility_tier1_open():
    # Tier 1 user, inside roster window -> Allowed (EVENT)
    now = datetime(2026, 2, 10, 10, 0, 0, tzinfo=timezone.utc)
    event = get_mock_event(now)
    
    # Fast forward to inside roster window (Event starts 24h from base 'now', Roster opens 4h before start)
    # Roster opens at base_now + 20h. 
    # Let's verify with a new 'now' that is strictly inside the window.
    
    event_start = event["roster_sign_up_open"] + timedelta(hours=4)
    roster_open_time = event["roster_sign_up_open"]
    
    current_time = event["roster_sign_up_open"] + timedelta(minutes=1)
    
    user_groups = ["group_roster"]
    
    # Since event is a mock, `status` may be None or "SCHEDULED".
    event["status"] = "OPEN_FOR_ROSTER" # explicitly enforce mock behavior
    
    result = check_signup_eligibility(event, user_groups, current_time)
    assert result["allowed"] == True
    assert result["target_list"] == "EVENT" 
    # Note: logic might return EVENT or WAITLIST depending on count, but eligibility just says "Go ahead, try to join event list" 
    # logic.py usually returns the intended *initial* target, which for Tier 1 is EVENT. 
    # The actual list insertion logic in main.py handles full/not full.
    # WAIT! Check implementation plan. 
    # "If allowed, insert into database with returned target_list."
    # So logic needs to suggest. 
    
def test_signup_eligibility_tier2_holding():
    # Tier 2 user, inside reserve window but before final scheduling -> HOLDING
    now = datetime(2026, 2, 10, 10, 0, 0, tzinfo=timezone.utc)
    event = get_mock_event(now) # Reserve opens NOW.
    
    user_groups = ["group_p1"]
    event["status"] = "OPEN_FOR_RESERVES"
    
    result = check_signup_eligibility(event, user_groups, now + timedelta(minutes=1))
    assert result["allowed"] == True
    assert result["target_list"] == "WAITLIST_HOLDING"

def test_signup_eligibility_tier3_post_scheduling():
    # Tier 3 user, AFTER final scheduling -> Waitlist/Event directly
    now = datetime(2026, 2, 10, 10, 0, 0, tzinfo=timezone.utc)
    event = get_mock_event(now)
    
    # Final sched is 2h before event. Event is 24h from now.
    # So 22h from now.
    
    current_time = event["final_reserve_scheduling"] + timedelta(minutes=1)
    
    user_groups = ["group_p2"]
    event["status"] = "FINAL_ORDERING"
    
    result = check_signup_eligibility(event, user_groups, current_time)
    assert result["allowed"] == True
    assert result["target_list"] == "EVENT" # Or generic "try to join"

def test_signup_eligibility_non_member():
    now = datetime(2026, 2, 10, 10, 0, 0, tzinfo=timezone.utc)
    event = get_mock_event(now)
    
    user_groups = ["random_group"]
    
    result = check_signup_eligibility(event, user_groups, now)
    assert result["allowed"] == False
    assert "No valid membership" in result["error_message"]

def test_randomize_holding_queue_logic():
    users = [
        {"id": "p1_1", "tier": 2},
        {"id": "p1_2", "tier": 2},
        {"id": "p2_1", "tier": 3},
        {"id": "p2_2", "tier": 3},
        {"id": "other", "tier": 1},
    ]
    
    sorted_users = randomize_holding_queue(users)
    
    assert len(sorted_users) == 5
    
    # Tier 2s come first
    assert sorted_users[0]["tier"] == 2
    assert sorted_users[1]["tier"] == 2
    
    # Tier 3s come next
    assert sorted_users[2]["tier"] == 3
    assert sorted_users[3]["tier"] == 3
    
    # Others at the end
    assert sorted_users[4]["tier"] == 1
