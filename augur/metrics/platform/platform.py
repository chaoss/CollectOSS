"""
Metrics that provide data about platform & their associated activity
"""

from augur.util import add_metrics

def create_platform_metrics(metrics):
    add_metrics(metrics, __name__)
