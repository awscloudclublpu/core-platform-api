from datetime import datetime
from typing import Optional
from .base import EventBase
from .enums import EventStatus


class EventResponse(EventBase):
    id: str

    short_description: Optional[str] = None
    status: EventStatus

    start_time: datetime
    end_time: datetime

from datetime import datetime
from typing import Optional
from .base import EventBase
from .enums import EventStatus


class EventDetails(EventBase):
    id: str

    short_description: Optional[str] = None
    description: Optional[str] = None
    agenda: Optional[str] = None
    rules: Optional[str] = None
    contact_email: Optional[str] = None

    status: EventStatus

    created_by: str           # organizer user_id
    registered_count: int

    created_at: datetime
    updated_at: datetime
