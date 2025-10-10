from enum import Enum

class ScheduleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
