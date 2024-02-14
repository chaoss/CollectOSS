
from enum import Enum

class CollectionState(Enum):
    """
    Enum of possible states a repository's collection
    can have whether it is core, secondary, facade, etc.

    Attributes:

    SUCCESS: State of success for the jobs in that collection hook
    PENDING: Means the repo has not had collection run at all
    ERROR: The collection hook has crashed
    COLLECTING: The collection hook is running
    INITIALIZING: Only for facade, indicates the repo is being cloned via git
    UPDATE: Only for facade, indicates the repo has been cloned
    FAILED_CLONE: Only for facade, indicates the clone has failed (usually 404)
    STANDBY: Indicates the repo has been paused 
    IGNORE: Repo has encountered an error and we will not try again (usually 404)
    """

    SUCCESS = "Success"
    PENDING = "Pending"
    ERROR = "Error"
    COLLECTING = "Collecting"
    INITIALIZING = "Initializing"
    UPDATE = "Update"
    FAILED_CLONE = "Failed Clone"
    STANDBY = "Standby"
    IGNORE = "Ignore"
