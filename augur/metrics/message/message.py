"""
Metrics that provide data about messages (of any form) & their associated activity
"""

import datetime
import sqlalchemy as s
import pandas as pd
from augur.util import logger, annotate, add_metrics

def create_message_metrics(metrics):
    add_metrics(metrics, __name__)
