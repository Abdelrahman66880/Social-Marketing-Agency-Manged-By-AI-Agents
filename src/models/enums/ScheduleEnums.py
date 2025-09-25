from enum import Enum

class ScheduleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class DayOfWeek(str, Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"
