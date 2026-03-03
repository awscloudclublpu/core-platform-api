from typing import Optional

from models.event.db import EventContent
from .enums import EventLevel, RegistrationMode
from datetime import datetime
from .base import EventBase
from pydantic import BaseModel, Field


class EventCreateRequest(EventBase, EventContent):
    pass


class EventUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=200)
    level: Optional[EventLevel] = None

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    location: Optional[str] = None
    banner_url: Optional[str] = None

    registration_mode: Optional[RegistrationMode] = None
    meetup_url: Optional[str] = None

    price: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = None
    capacity: Optional[int] = Field(default=None, gt=0)

    short_description: Optional[str] = Field(default=None, max_length=300)
    description: Optional[str] = None
    agenda: Optional[str] = None
    rules: Optional[str] = None
    contact_email: Optional[str] = None