from enum import Enum
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

class EventStatus(str, Enum):
    NOT_YET_OPEN = "NOT_YET_OPEN"
    OPEN_FOR_ROSTER = "OPEN_FOR_ROSTER"
    OPEN_FOR_RESERVES = "OPEN_FOR_RESERVES"
    PRELIMINARY_ORDERING = "PRELIMINARY_ORDERING"
    FINAL_ORDERING = "FINAL_ORDERING"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"

class EventStatusDeterminant(str, Enum):
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"

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
    status_determinant: EventStatusDeterminant = EventStatusDeterminant.AUTOMATIC
    duration: Optional[str] = None # Pydantic will serialize INTERVAL/timedelta to ISO string or similar
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

class EventTypeCreate(BaseModel):
    name: str
    day_of_week: int  # 0=Sunday, 6=Saturday
    time_of_day: str  # TIME format "HH:MM:SS"
    time_zone: str = "America/Los_Angeles"
    max_signups: int = 15
    roster_sign_up_open_minutes: int = 4320  # 3 days
    reserve_sign_up_open_minutes: int = 720  # 12 hours
    initial_reserve_scheduling_minutes: int = 420  # 7 hours
    final_reserve_scheduling_minutes: int = 180  # 3 hours
    roster_user_group: Optional[str] = None  # UUID
    reserve_first_priority_user_group: Optional[str] = None  # UUID
    reserve_second_priority_user_group: Optional[str] = None  # UUID

class EventTypeUpdate(BaseModel):
    name: Optional[str] = None
    day_of_week: Optional[int] = None
    time_of_day: Optional[str] = None
    time_zone: Optional[str] = None
    max_signups: Optional[int] = None
    roster_sign_up_open_minutes: Optional[int] = None
    reserve_sign_up_open_minutes: Optional[int] = None
    initial_reserve_scheduling_minutes: Optional[int] = None
    final_reserve_scheduling_minutes: Optional[int] = None
    roster_user_group: Optional[str] = None
    reserve_first_priority_user_group: Optional[str] = None
    reserve_second_priority_user_group: Optional[str] = None
