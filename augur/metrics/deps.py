#SPDX-License-Identifier: MIT
"""
Metrics that provide data about with insight detection and reporting
"""

import sqlalchemy as s
import pandas as pd
from augur.util import register_metric

@register_metric()
def deps(self, repo_group_id, repo_id=None):
	depsSQL = s.sql.text("""
    	SELECT * FROM augur_data.dependencies
	""")

	results = pd.read_sql(depsSQL, self.database)

	return results
