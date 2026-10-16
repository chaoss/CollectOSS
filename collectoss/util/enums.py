from enum import Enum

class ForgePlatformType(Enum):
    """Identification values for different known forges.
    Intended for helping identify the relevant API endpoints and tasks to use for collection"""
    UNRESOLVEABLE = 0
    GITHUB = 1
    GITLAB = 2