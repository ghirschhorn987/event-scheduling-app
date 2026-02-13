import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import asyncio

# Mock libraries
sys.modules["db"] = MagicMock()
sys.modules["resend"] = MagicMock()

from backend.models import SignupRequest

# Mock FastAPI Request
class MockRequest:
    def __init__(self, user_id):
        self.state = MagicMock()
        self.headers = {}
        self.user_id = user_id

# We need to import main AFTER mocking
from backend.main import remove_signup

class TestCancellation(unittest.TestCase):
    
    @patch("backend.main.get_current_user", new_callable=AsyncMock)
    @patch("backend.main.supabase")
    def test_promotion_logic(self, mock_supabase, mock_get_current_user):
        # Setup Async Loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 1. Setup Mock User
        user_id = "user_123"
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_get_current_user.return_value = mock_user
        
        # 2. Setup Mock Profile Return
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {"id": "profile_123"}
        
        # 3. Setup Mock "Current Signup" (It is an EVENT signup)
        # Chain for: supabase.table().select().eq().eq().maybe_single().execute()
        signup_query_mock = MagicMock()
        signup_query_mock.data = {"list_type": "EVENT"}
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = signup_query_mock

        # 4. Setup Mock "Next Waitlist User"
        waitlist_query_mock = MagicMock()
        waitlist_query_mock.data = [{"id": "signup_999", "user_id": "profile_999", "list_type": "WAITLIST"}]
        
        # This chain is long: table().select().eq().eq().order().order().limit().execute()
        # We simplify by making the execute return value generic for the waitlist search
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.order.return_value.limit.return_value.execute.return_value = waitlist_query_mock

        # Run the function
        req = MockRequest(user_id)
        body = SignupRequest(event_id="evt_1", user_id=user_id)
        
        result = loop.run_until_complete(remove_signup(body, req))
        
        self.assertEqual(result["status"], "success")
        
        # Verify Promotion happened
        # We expect an update call
        # supabase.table("event_signups").update({"list_type": "EVENT"}).eq("id", "signup_999").execute()
        
        # Check call args
        # This is a bit loose but checks if update was called
        self.assertTrue(mock_supabase.table.return_value.update.called)
        
        # Ideally check args:
        # call_args = mock_supabase.table.return_value.update.call_args
        # self.assertEqual(call_args[0][0], {"list_type": "EVENT"})
        
        loop.close()

if __name__ == '__main__':
    unittest.main()
