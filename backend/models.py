from enum import Enum
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SignupRequest(BaseModel):
    event_id: str
    user_id: str  # In a real app, we'd get this from the auth token, but for now we'll accept it
    is_guest: Optional[bool] = False
    guest_name: Optional[str] = None
    signup_id: Optional[str] = None # Used for removing an explicit signup

class ScheduleResponse(BaseModel):
    status: str
    message: str
    updated_count: int

class UserGroupType(str, Enum):
    EVENT_ELIGIBILITY = "EVENT_ELIGIBILITY"
    APPLICATION_ROLE = "APPLICATION_ROLE"
    USER_CHARACTERISTIC = "USER_CHARACTERISTIC"
    OTHER = "OTHER"

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
    reserve_second_priority_user_group: Optional[str] = None
    duration_minutes: int = 120 # Default 2 hours

class Event(BaseModel):
    id: str
    event_type_id: str
    event_date: datetime
    status: str
    status_determinant: EventStatusDeterminant = EventStatusDeterminant.AUTOMATIC
    # Enriched fields (joined from EventType for API result)
    name: Optional[str] = None
    max_signups: Optional[int] = None
    duration: Optional[str] = None # Enriched from EventType
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

class BulkUserCreate(BaseModel):
    full_name: str
    email: str
    groups: Optional[List[str]] = []

class GroupMemberAction(BaseModel):
    email: str

class GroupMembersAction(BaseModel):
    profile_ids: List[str]

class UserGroupsUpdate(BaseModel):
    group_ids: List[str]

class UserGroupMetadataUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    google_group_id: Optional[str] = None
    group_email: Optional[str] = None
    guest_limit: Optional[int] = None
    group_type: Optional[str] = None

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
    duration_minutes: int = 120

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
    duration_minutes: Optional[int] = None

class CancelledDate(BaseModel):
    date: str # YYYY-MM-DD
    reason: Optional[str] = None

class EventStatusUpdate(BaseModel):
    status: str
    status_determinant: str # MANUAL or AUTOMATIC

class AdminEventUserAdd(BaseModel):
    profile_id: Optional[str] = None
    is_guest: bool = False
    guest_name: Optional[str] = None
    target_list: str  # "EVENT", "WAITLIST", "WAITLIST_HOLDING"

class AdminEventUserReorderItem(BaseModel):
    signup_id: str
    sequence_number: int

class AdminEventUserReorderRequest(BaseModel):
    items: List[AdminEventUserReorderItem]

class AdminEventUserMove(BaseModel):
    target_list: str  # "EVENT", "WAITLIST", "WAITLIST_HOLDING"
