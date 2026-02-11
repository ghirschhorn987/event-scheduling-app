
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure backend matches path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email_service import EmailService

@pytest.fixture
def email_service():
    # Patch the module-level variable to enable "real" sending logic (which we mock)
    with patch('email_service.RESEND_API_KEY', 're_test_key'):
        yield EmailService()

def test_send_acknowledgement(email_service):
    with patch('resend.Emails.send') as mock_send:
        mock_send.return_value = {"id": "test-id"}
        
        # We need to ensure resend.api_key is set because EmailService.__init__ might have run before patching
        import resend
        resend.api_key = "re_test"

        resp = email_service.send_user_acknowledgement("test@example.com", "John Doe")
        assert resp is not None
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        sent_params = args[0]
        assert sent_params['to'] == ["test@example.com"]
        assert "John Doe" in sent_params['html']

def test_send_rejection_reason(email_service):
    with patch('resend.Emails.send') as mock_send:
        mock_send.return_value = {"id": "test-id"}
        import resend
        resend.api_key = "re_test"
        
        resp = email_service.send_rejection_reason("test@example.com", "Spam")
        assert resp is not None
        mock_send.assert_called_once()

def test_send_access_granted(email_service):
    with patch('resend.Emails.send') as mock_send:
        mock_send.return_value = {"id": "test-id"}
        import resend
        resend.api_key = "re_test"
        
        resp = email_service.send_access_granted("test@example.com", "Jane Doe")
        assert resp is not None
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        sent_params = args[0]
        assert sent_params['to'] == ["test@example.com"]
        assert "Welcome to Skeddle" in sent_params['subject']
        assert "Jane Doe" in sent_params['html']
