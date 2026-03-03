from datetime import datetime
from typing import Optional

from models.event.db import EventContent
from models.event.base import EventBase
from models.event.enums import EventStatus, RegistrationMode, EventLevel
from pydantic import BaseModel


class EventResponse(BaseModel):
    id: str
    title: str
    short_description: Optional[str]
    banner_url: Optional[str]

    start_time: datetime
    end_time: datetime

    location: Optional[str]
    level: EventLevel
    registration_mode: RegistrationMode

    price: Optional[float]
    currency: Optional[str]

class EventDetails(EventBase, EventContent):
    id: str

    status: EventStatus

    attendance_enabled: bool
    certificate_enabled: bool

    registered_count: int

    created_at: datetime
