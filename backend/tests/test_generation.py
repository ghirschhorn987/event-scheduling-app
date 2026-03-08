import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta
from logic import generate_future_events

def test_generate_future_events_basic():
    """
    Test that the generator creates events for the correct days of week.
    """
    mock_supabase = MagicMock()
    
    # 1. Mock Event Types
    mock_event_types = MagicMock()
    mock_event_types.data = [{
        "id": "t1",
        "name": "Tuesday Basketball",
        "day_of_week": 2, # Tuesday
        "time_of_day": "18:00:00",
        "max_signups": 15
    }]
    
    # 2. Mock Blackout Dates
    mock_blackouts = MagicMock()
    mock_blackouts.data = []
    
    # 3. Mock Check Existing (Empty)
    mock_existing = MagicMock()
    mock_existing.data = []
    
    # 4. Mock Insert Success
    mock_insert_res = MagicMock()
    mock_insert_res.data = [{"id": "new-event-789"}]

    # Set up the chain of mocks
    # First call: table("event_types").select("*").execute()
    # Second call: table("cancelled_dates").select("date").execute()
    # Third call: table("events").select("id").eq().eq().execute()
    
    # We'll use a side_effect on the final .execute() for the select chains
    mock_supabase.table.return_value.select.return_value.execute.side_effect = [
        mock_event_types,
        mock_blackouts
    ]
    
    # For the chained eq calls:
    mock_eq_chain = mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value
    mock_eq_chain.execute.return_value = mock_existing
    
    # For the insert call:
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert_res
    
    with patch('logic.datetime') as mock_date:
        # Mock "today" as Monday, 2026-03-02
        mock_date.now.return_value = datetime(2026, 3, 2, 10, 0, 0, tzinfo=timezone.utc)
        mock_date.fromisoformat = datetime.fromisoformat
        mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        count = generate_future_events(mock_supabase, days_ahead_to_ensure=7)
        
        # Should have found 1 Tuesday (2026-03-03)
        assert count == 1
        
        mock_supabase.table.return_value.insert.assert_called_once()
        payload = mock_supabase.table.return_value.insert.call_args[0][0]
        assert payload["event_type_id"] == "t1"
        assert "2026-03-03T18:00:00" in payload["event_date"]
        assert payload["status"] == "NOT_YET_OPEN"

def test_generate_future_events_with_blackout():
    """
    Test that matching blackout dates creates CANCELLED events.
    """
    mock_supabase = MagicMock()
    
    mock_event_types = MagicMock()
    mock_event_types.data = [{
        "id": "t1",
        "name": "Tuesday Basketball",
        "day_of_week": 2,
        "time_of_day": "18:00:00",
        "max_signups": 15
    }]
    
    mock_blackouts = MagicMock()
    mock_blackouts.data = [{"date": "2026-03-03"}]
    
    mock_existing = MagicMock()
    mock_existing.data = []
    
    mock_insert_res = MagicMock()
    mock_insert_res.data = [{"id": "new-event-cancelled"}]

    mock_supabase.table.return_value.select.return_value.execute.side_effect = [
        mock_event_types,
        mock_blackouts
    ]
    
    mock_eq_chain = mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value
    mock_eq_chain.execute.return_value = mock_existing
    
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert_res
    
    with patch('logic.datetime') as mock_date:
        # Mock "today" as Monday, 2026-03-02
        mock_date.now.return_value = datetime(2026, 3, 2, 10, 0, 0, tzinfo=timezone.utc)
        mock_date.fromisoformat = datetime.fromisoformat
        mock_date.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        count = generate_future_events(mock_supabase, days_ahead_to_ensure=7)
        
        assert count == 1
        
        # Verify it attempted to insert CANCELLED status
        mock_supabase.table.return_value.insert.assert_called_once()
        assert mock_supabase.table.return_value.insert.call_args[0][0]["status"] == "CANCELLED"
