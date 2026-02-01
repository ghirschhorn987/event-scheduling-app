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

class Event(BaseModel):
    id: str
    name: str
    status: str
    max_signups: int
    event_date: datetime
    roster_sign_up_open: datetime
    waitlist_sign_up_open: datetime
    reserve_sign_up_open: datetime
    initial_reserve_scheduling: datetime
    final_reserve_scheduling: datetime
