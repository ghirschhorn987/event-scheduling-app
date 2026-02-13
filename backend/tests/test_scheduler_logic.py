import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta

# Mock Supabase before importing main
import sys
sys.modules["db"] = MagicMock()
sys.modules["db"].supabase = MagicMock()

from backend.logic import determine_event_status, check_signup_eligibility, randomize_holding_queue

class TestSchedulerLogic(unittest.TestCase):
    
    def test_determine_event_status(self):
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        event = {
            "roster_sign_up_open": "2024-01-01T10:00:00+00:00",
            "reserve_sign_up_open": "2024-01-01T11:00:00+00:00",
            "initial_reserve_scheduling": "2024-01-01T13:00:00+00:00",
            "final_reserve_scheduling": "2024-01-01T14:00:00+00:00",
            "event_date": "2024-01-01T18:00:00+00:00"
        }
        
        # Test OPEN_FOR_RESERVES (11:00 - 13:00)
        self.assertEqual(determine_event_status(event, now), "OPEN_FOR_RESERVES")
        
        # Test PRELIMINARY_ORDERING (13:00 - 14:00)
        now_prelim = datetime(2024, 1, 1, 13, 30, 0, tzinfo=timezone.utc)
        self.assertEqual(determine_event_status(event, now_prelim), "PRELIMINARY_ORDERING")
        
    def test_randomize_holding_queue(self):
        users = [
            {"id": 1, "tier": 2, "name": "T2_A"},
            {"id": 2, "tier": 3, "name": "T3_A"},
            {"id": 3, "tier": 2, "name": "T2_B"},
            {"id": 4, "tier": 3, "name": "T3_B"},
        ]
        
        sorted_users = randomize_holding_queue(users)
        
        # Check Tiers are grouped: All T2 before All T3
        t2_indices = [i for i, u in enumerate(sorted_users) if u["tier"] == 2]
        t3_indices = [i for i, u in enumerate(sorted_users) if u["tier"] == 3]
        
        self.assertTrue(max(t2_indices) < min(t3_indices), "Tier 2 should come before Tier 3")
        self.assertEqual(len(sorted_users), 4)

    def test_check_eligibility_open_for_roster(self):
        event = {"status": "OPEN_FOR_ROSTER", "roster_user_group": "Roster"}
        
        # Roster Member
        res = check_signup_eligibility(event, ["Roster"], datetime.now())
        self.assertTrue(res["allowed"])
        self.assertEqual(res["target_list"], "EVENT")
        
        # Non Roster (even if Tier 2)
        event["reserve_first_priority_user_group"] = "Reserves"
        res = check_signup_eligibility(event, ["Reserves"], datetime.now())
        self.assertFalse(res["allowed"])

if __name__ == '__main__':
    unittest.main()
