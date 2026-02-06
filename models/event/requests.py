from typing import Optional
from .base import EventBase


class EventCreateRequest(EventBase):
    short_description: Optional[str] = None
    description: Optional[str] = None


class EventUpdateRequest(EventBase):
    title: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
