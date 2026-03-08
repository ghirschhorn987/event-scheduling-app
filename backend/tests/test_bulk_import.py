import pytest
import httpx
import uuid
from httpx import AsyncClient
from main import app, supabase
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_admin_request():
    with patch("main.get_current_admin", return_value=MagicMock()):
        yield

@pytest.fixture
def mock_email_service():
    with patch("main.email_service.send_access_granted", return_value=True) as mock_send:
        yield mock_send

@pytest.mark.asyncio
async def test_bulk_pre_approve_users(mock_admin_request, mock_email_service):
    # Setup: Create a test group
    group_name = f"Test Group {uuid.uuid4().hex[:8]}"
    group_res = supabase.table("user_groups").insert({"name": group_name}).execute()
    group_id = group_res.data[0]['id']
    
    payload = [
        {
            "full_name": "CSV User 1",
            "email": "csv1@test.com",
            "groups": [group_name, "Non Existent Group"]
        },
        {
            "full_name": "CSV User 2",
            "email": "csv2@test.com",
            "groups": []
        }
    ]
    
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/admin/users/bulk-pre-approve", json=payload)
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["success_count"] == 2
    assert len(data["errors"]) == 0
    
    # Verify profiles were created
    p1 = supabase.table("profiles").select("*").eq("email", "csv1@test.com").execute()
    assert len(p1.data) == 1
    assert p1.data[0]["name"] == "CSV User 1"
    
    p2 = supabase.table("profiles").select("*").eq("email", "csv2@test.com").execute()
    assert len(p2.data) == 1
    
    # Verify profile_groups were created for User 1
    pg1 = supabase.table("profile_groups").select("*").eq("profile_id", p1.data[0]["id"]).execute()
    assert len(pg1.data) == 1
    assert pg1.data[0]["group_id"] == group_id
    
    # Verify registration_requests were created for history
    r1 = supabase.table("registration_requests").select("*").eq("email", "csv1@test.com").execute()
    assert len(r1.data) == 1
    assert r1.data[0]["status"] == "APPROVED"
    assert r1.data[0]["admin_notes"] == "Added via CSV Bulk Import"
    
    # Check emails triggered
    assert mock_email_service.call_count == 2
    
    # Cleanup
    supabase.table("registration_requests").delete().in_("email", ["csv1@test.com", "csv2@test.com"]).execute()
    supabase.table("profiles").delete().in_("email", ["csv1@test.com", "csv2@test.com"]).execute()
    supabase.table("user_groups").delete().eq("id", group_id).execute()
