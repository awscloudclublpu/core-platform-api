from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from .base import EventBase
from .enums import EventStatus

class EventContent(BaseModel):
    short_description: Optional[str] = Field(default=None, max_length=300)
    description: Optional[str] = None
    agenda: Optional[str] = None
    rules: Optional[str] = None
    contact_email: Optional[str] = None

class EventDB(EventBase, EventContent):
    id: str

    status: EventStatus = EventStatus.draft

    attendance_enabled: bool = False
    certificate_enabled: bool = False

    registered_count: int = 0

    created_by: str
    created_at: datetime
    updated_at: datetime
