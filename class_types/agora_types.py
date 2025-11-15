from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class TTSVendor(str, Enum):
    MICROSOFT = "microsoft"
    ELEVENLABS = "elevenlabs"

class ASRVendor(str, Enum):
    DEEPGRAM = "deepgram"
    MICROSOFT = "microsoft"
    ARES = "ares"

class TTSConfig(BaseModel):
    vendor: TTSVendor
    params: dict

class ASRConfig(BaseModel):
    vendor: ASRVendor
    params: dict

class AgentResponse(BaseModel):
    agent_id: str
    create_ts: int
    status: str
    channel_name: Optional[str] = None
    token: Optional[str] = None

class EventPlannerRequest(BaseModel):
    requester_id: str
    channel_name: Optional[str] = None
    event_type: Optional[str] = None
    attendee_count: Optional[int] = None
    budget_range: Optional[str] = None
    preferred_date: Optional[str] = None
    location_preference: Optional[str] = None
    special_requirements: Optional[str] = None
    user_uid: Optional[str] = "12345"

class RemoveAgentRequest(BaseModel):
    agent_id: str

class EventDetails(BaseModel):
    event_id: str
    event_type: str
    attendee_count: int
    budget_range: str
    preferred_date: str
    location: str
    status: str
    rsvp_count: int
    created_at: str