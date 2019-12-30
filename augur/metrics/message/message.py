"""
Metrics that provide data about messages (of any form) & their associated activity
"""

from augur.util import add_metrics

def create_message_metrics(metrics):
    add_metrics(metrics, __name__)
