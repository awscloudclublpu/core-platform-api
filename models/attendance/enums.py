from enum import Enum

class ActionType(str, Enum):
    checkin = "checkin"
    checkout = "checkout"