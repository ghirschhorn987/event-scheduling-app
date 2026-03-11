import pytest
import sys
import os
from datetime import datetime, timedelta, timezone

# Add parent directory to path to import logic
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import enrich_event, randomize_holding_queue, promote_from_holding

def test_enrich_event():
    # Helper to create a naive datetime and force it to match logic's expectation if needed
    base_date = datetime(2026, 2, 10, 19, 0, 0)
    base_iso = base_date.isoformat() # "2026-02-10T19:00:00"
    
    event_data = {
        "event_date": base_iso,
        "event_types": {
            "name": "Test Class",
            "max_signups": 15,
            "roster_sign_up_open_minutes": 60,
            "reserve_sign_up_open_minutes": 120,
            "initial_reserve_scheduling_minutes": 30,
            "final_reserve_scheduling_minutes": 10
        }
    }
    
    enriched = enrich_event(event_data)
    
    assert enriched["name"] == "Test Class"
    assert enriched["max_signups"] == 15
    
    # Check calculated times
    # Note: logic.py replaces 'Z' with +00:00 but our input didn't have Z. 
    # Logic handles ISO string.
    
    # We expect dates to be roughly correct relative to event_date
    event_dt = datetime.fromisoformat(base_iso)
    
    assert enriched["roster_sign_up_open"] == event_dt - timedelta(minutes=60)
    assert enriched["reserve_sign_up_open"] == event_dt - timedelta(minutes=120)

def test_randomize_holding_queue_sorting():
    # Only Tier 2 and Tier 3 matter for randomization logic
    users = [
        {"id": "u1", "tier": 3},
        {"id": "u2", "tier": 2},
        {"id": "u3", "tier": 3},
        {"id": "u4", "tier": 2},
        {"id": "u5", "tier": 1} # Others appended at the end
    ]
    
    sorted_queue = randomize_holding_queue(users)
    
    assert len(sorted_queue) == 5
    
    # Tier 2 should be first, then Tier 3, then Others
    assert sorted_queue[0]["tier"] == 2
    assert sorted_queue[1]["tier"] == 2
    
    assert sorted_queue[2]["tier"] == 3
    assert sorted_queue[3]["tier"] == 3
    
    # Others at the end
    assert sorted_queue[4]["tier"] == 1

def test_promote_from_holding_all_roster():
    queue = [{"id": "u1"}, {"id": "u2"}]
    current_roster = 10
    max_signups = 15
    current_waitlist = 0
    
    updates = promote_from_holding(queue, current_roster, max_signups, current_waitlist)
    
    assert len(updates) == 2
    assert updates[0]["list_type"] == "EVENT"
    assert updates[0]["sequence_number"] == 11
    
    assert updates[1]["list_type"] == "EVENT"
    assert updates[1]["sequence_number"] == 12

def test_promote_from_holding_overflow_to_waitlist():
    queue = [{"id": "u1"}, {"id": "u2"}, {"id": "u3"}]
    current_roster = 14
    max_signups = 15
    current_waitlist = 5
    
    updates = promote_from_holding(queue, current_roster, max_signups, current_waitlist)
    
    # u1 -> Roster (15)
    # u2 -> Waitlist (6)
    # u3 -> Waitlist (7)
    
    assert updates[0]["list_type"] == "EVENT"
    assert updates[0]["sequence_number"] == 15
    
    assert updates[1]["list_type"] == "WAITLIST"
    assert updates[1]["sequence_number"] == 6
    
    assert updates[2]["list_type"] == "WAITLIST"
    assert updates[2]["sequence_number"] == 7
