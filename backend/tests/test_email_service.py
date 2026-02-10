
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure backend matches path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email_service import EmailService

@pytest.fixture
def email_service():
    return EmailService()

def test_send_acknowledgement(email_service):
    with patch('resend.Emails.send') as mock_send:
        mock_send.return_value = {"id": "test-id"}
        # Force API Key presence for test (or use mock if not present)
        with patch('os.environ.get', return_value='re_123'):
             # Re-init to pick up key
             service = EmailService()
             # Manually set key because of how the class inits
             import resend
             resend.api_key = "re_test"
             
             resp = service.send_user_acknowledgement("test@example.com", "John Doe")
             assert resp is not None
             mock_send.assert_called_once()
             args, kwargs = mock_send.call_args
             assert kwargs['params']['to'] == ["test@example.com"]
             assert "John Doe" in kwargs['params']['html']

def test_send_rejection_reason(email_service):
    with patch('resend.Emails.send') as mock_send:
        mock_send.return_value = {"id": "test-id"}
        import resend
        resend.api_key = "re_test"
        
        resp = email_service.send_rejection_reason("test@example.com", "Spam")
        assert resp is not None
        mock_send.assert_called_once()
