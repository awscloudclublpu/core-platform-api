from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional
from models.event.enums import EventType, EventLevel


class EventBase(BaseModel):
    title: str = Field(min_length=3, max_length=200)

    event_type: EventType = EventType.free
    level: EventLevel = EventLevel.beginner

    price: Optional[float] = Field(default=None, gt=0)
    currency: str = "INR"

    start_time: datetime
    end_time: datetime

    location: Optional[str] = None
    banner_url: Optional[str] = None

    capacity: Optional[int] = Field(
        default=None,
        gt=0,
        description="Max attendees; None means unlimited",
    )

    @model_validator(mode="after")
    def validate_event(self):
        if self.event_type == EventType.paid:
            if self.price is None or self.currency is None:
                raise ValueError("Paid events require price and currency")
        else:
            if self.price is not None or self.currency is not None:
                raise ValueError("Free events cannot have price or currency")

        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")

        return self
