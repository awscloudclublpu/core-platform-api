from enum import Enum

class EventStatus(str, Enum):
    draft = "draft"
    published = "published"
    cancelled = "cancelled"

class EventLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class RegistrationMode(str, Enum):
    external = "external"
    internal = "internal"