from datetime import datetime
from typing import Optional
from .base import EventBase
from .enums import EventStatus


class EventDB(EventBase):
    id: str

    short_description: Optional[str] = None
    description: Optional[str] = None
    agenda: Optional[str] = None
    rules: Optional[str] = None
    contact_email: Optional[str] = None

    status: EventStatus = EventStatus.draft

    created_by: str

    registered_count: int = 0

    created_at: datetime
    updated_at: datetime
