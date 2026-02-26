from enum import Enum


class UserRole(str, Enum):
    attendee = "attendee"
    manager = "manager"
    core = "core"
