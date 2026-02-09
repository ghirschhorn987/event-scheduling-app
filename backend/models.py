from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SignupRequest(BaseModel):
    event_id: str
    user_id: str  # In a real app, we'd get this from the auth token, but for now we'll accept it

class ScheduleResponse(BaseModel):
    status: str
    message: str
    updated_count: int

class EventType(BaseModel):
    id: str
    name: str
    day_of_week: int
    time_of_day: str  # Time object or string? Pydantic handles str usually
    time_zone: str
    max_signups: int
    roster_sign_up_open_minutes: int
    reserve_sign_up_open_minutes: int
    initial_reserve_scheduling_minutes: int
    final_reserve_scheduling_minutes: int

class Event(BaseModel):
    id: str
    event_type_id: str
    event_date: datetime
    status: str
    # Enriched fields (joined from EventType for API response)
    name: Optional[str] = None
    max_signups: Optional[int] = None
    # Calculated timestamps based on event_date - minutes
    roster_sign_up_open: Optional[datetime] = None
    reserve_sign_up_open: Optional[datetime] = None
    initial_reserve_scheduling: Optional[datetime] = None
    final_reserve_scheduling: Optional[datetime] = None
    # Counts
    counts: Optional[dict] = None # { "roster": int, "waitlist": int, "holding": int }

class RegistrationRequest(BaseModel):
    full_name: str
    email: str
    affiliation: str
    referral: Optional[str] = None

class RegistrationUpdate(BaseModel):
    request_id: str
    action: str  # 'APPROVE' or 'DECLINE' or 'INFO'
    role: Optional[str] = None # For approval (Primary, Secondary, etc.)
    note: Optional[str] = None
