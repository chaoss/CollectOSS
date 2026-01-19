"""
Shared models and enums for the improved collection system.
"""

from enum import Enum


class TaskRunState(str, Enum):
    """Enum for task run states."""
    PENDING = 'Pending'
    QUEUED = 'Queued'
    COLLECTING = 'Collecting'
    COMPLETE = 'Complete'
    FAILED = 'Failed'


class CollectionState(str, Enum):
    """Enum for collection states."""
    COLLECTING = 'Collecting'
    COMPLETE = 'Complete'
    FAILED = 'Failed'
