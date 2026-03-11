import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, get_current_admin

client = TestClient(app)

# Mock get_current_admin in tests via patch
@pytest.fixture(autouse=True)
def mock_admin():
    with patch("main.get_current_admin", new_callable=AsyncMock) as mock:
        mock_user = MagicMock()
        mock_user.id = "admin_123"
        mock_user.email = "admin@test.com"
        mock.return_value = mock_user
        yield mock

@patch("main.supabase")
def test_list_admin_event_users(mock_supabase):
    mock_res = MagicMock()
    mock_res.data = [{"id": "signup_1", "user_id": "user_1", "list_type": "EVENT", "sequence_number": 1}]
    # Chain: supabase.table().select().eq().order().execute()
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_res
    
    response = client.get("/api/admin/events/evt_1/users")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert len(response.json()["data"]) == 1

@patch("main.supabase")
def test_add_admin_event_user(mock_supabase):
    # Mock count
    count_res = MagicMock()
    count_res.count = 2
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = count_res
    
    # Mock insert
    insert_res = MagicMock()
    insert_res.data = [{"id": "signup_new"}]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = insert_res
    
    payload = {
        "profile_id": "user_99",
        "is_guest": False,
        "target_list": "WAITLIST"
    }
    
    response = client.post("/api/admin/events/evt_1/users", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["id"] == "signup_new"

@patch("main.supabase")
def test_remove_admin_event_user(mock_supabase):
    # Mock current signup
    current_res = MagicMock()
    current_res.data = {"id": "signup_2", "user_id": "user_2", "is_guest": False, "list_type": "EVENT", "sequence_number": 2}
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = current_res
    
    # Mock guests (none)
    guests_res = MagicMock()
    guests_res.data = []
    
    # Needs to handle the sequence of calls: 
    # 1. select for current setup
    # 2. select for guests
    # 3. select for fresh data during loop
    # We can use side_effect or just return a generic that has everything
    # Let's just use side effect for the first execute() which is the maybe_single
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.side_effect = [
        current_res, # For current_res
        current_res  # For fresh_res inside loop
    ]
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = guests_res
    
    # Mock to_update
    update_res = MagicMock()
    update_res.data = [{"id": "signup_3", "sequence_number": 3}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.gt.return_value.execute.return_value = update_res
    
    # Mock delete output
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{"id": "signup_2"}]
    
    response = client.delete("/api/admin/events/evt_1/users/signup_2")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@patch("main.supabase")
def test_reorder_admin_event_users(mock_supabase):
    payload = {
        "list_type": "EVENT",
        "items": [
            {"signup_id": "signup_2", "sequence_number": 1},
            {"signup_id": "signup_1", "sequence_number": 2}
        ]
    }
    
    response = client.put("/api/admin/events/evt_1/users/reorder", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@patch("main.supabase")
def test_move_admin_event_user(mock_supabase):
    # Mock current signup
    current_res = MagicMock()
    current_res.data = {"list_type": "WAITLIST", "sequence_number": 1}
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = current_res
    
    # Mock new length
    count_res = MagicMock()
    count_res.count = 3
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = count_res
    
    # Mock to_update
    update_res = MagicMock()
    update_res.data = [{"id": "signup_w2", "sequence_number": 2}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.gt.return_value.execute.return_value = update_res
    
    payload = {"target_list": "EVENT"}
    response = client.put("/api/admin/events/evt_1/users/signup_w1/move", json=payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "moved to EVENT" in response.json()["message"]
