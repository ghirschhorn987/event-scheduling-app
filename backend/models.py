from pydantic import BaseModel
from typing import Optional, List
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
    roster_user_group: Optional[str] = None
    reserve_first_priority_user_group: Optional[str] = None
    reserve_second_priority_user_group: Optional[str] = None

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
    action: str  # 'APPROVED' or 'DECLINED' or 'INFO'
    groups: Optional[List[str]] = [] # For approval (List of group names)
    note: Optional[str] = None
    message: Optional[str] = None # Message to user for DECLINE or INFO actions

class GroupMemberAction(BaseModel):
    email: str

class GroupMembersAction(BaseModel):
    profile_ids: List[str]

class UserGroupsUpdate(BaseModel):
    group_ids: List[str]
