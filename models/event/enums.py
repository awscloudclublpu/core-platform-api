from enum import Enum

class EventStatus(str, Enum):
    draft = "draft"
    published = "published"
    cancelled = "cancelled"

class EventType(str, Enum):
    free = "free"
    paid = "paid"

class EventLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"