#SPDX-License-Identifier: MIT
"""
Metrics that provide data about with insight detection and reporting
"""

import sqlalchemy as s
import pandas as pd
from augur.util import register_metric

@register_metric()
def deps(self, repo_group_id, repo_id=None):
    results = []
    for x in range(10):
    	v = x*100
    	results.append([v, v+1])
    
    print("stuart - deps")
    return results
