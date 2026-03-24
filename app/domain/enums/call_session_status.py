from enum import Enum


class CallSessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
