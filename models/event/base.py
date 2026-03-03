from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional
from .enums import EventLevel, RegistrationMode

class EventBase(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    level: EventLevel = EventLevel.beginner

    start_time: datetime
    end_time: datetime

    location: Optional[str] = None
    banner_url: Optional[str] = None

    registration_mode: RegistrationMode

    meetup_url: Optional[str] = None

    price: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = None

    capacity: Optional[int] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_event(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")

        if self.registration_mode == RegistrationMode.external:
            if not self.meetup_url:
                raise ValueError("External events require meetup_url")
            if self.price is not None:
                raise ValueError("External events cannot have price")
            if self.capacity is not None:
                raise ValueError("External events should not define capacity")

        if self.registration_mode == RegistrationMode.internal:
            if self.price is not None and not self.currency:
                raise ValueError("Paid events require currency")

        return self