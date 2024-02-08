from enum import Enum

class CollectionState(Enum):
    SUCCESS = "Success"
    PENDING = "Pending"
    ERROR = "Error"
    COLLECTING = "Collecting"
    INITIALIZING = "Initializing"
    UPDATE = "Update"
    FAILED_CLONE = "Failed Clone"
    STANDBY = "Standby"
