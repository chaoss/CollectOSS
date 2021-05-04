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
    	SELECT b.repo_name as name, a.c as count
		FROM (SELECT repo_id, COUNT(cmt_author_email) as c FROM augur_data.commits GROUP BY repo_id) AS a
		JOIN
		augur_data.repo AS b
		ON a.repo_id=b.repo_id;
	""")

	results = pd.read_sql(depsSQL, self.database)

	return results
