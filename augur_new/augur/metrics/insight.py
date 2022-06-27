#SPDX-License-Identifier: MIT
"""
Metrics that provide data about with insight detection and reporting
"""

import sqlalchemy as s
import pandas as pd
from augur.util import register_metric

@register_metric(type="repo_group_only")
def top_insights(self, repo_group_id, num_repos=6):
    """
    Timeseries of pull request acceptance rate (expressed as the ratio of pull requests merged on a date to the count of pull requests opened on a date)

    :return: DataFrame with top insights across all repos
    """

    topInsightsSQL = s.sql.text("""
        SELECT rg_name, repo.repo_group_id, repo_insights.repo_id, repo_git, ri_metric, ri_field, ri_value AS value,
            ri_date AS date, ri_fresh AS discovered
        FROM repo_insights JOIN repo ON repo.repo_id = repo_insights.repo_id JOIN repo_groups ON repo.repo_group_id = repo_groups.repo_group_id
        WHERE repo_insights.repo_id IN (
            SELECT repo_id
            FROM repo
            WHERE repo_group_id = :repo_group_id
            AND repo_id IN (SELECT repo_id FROM repo_insights GROUP BY repo_id, ri_id HAVING 304 > count(repo_insights.repo_id) ORDER BY ri_id desc)
            LIMIT :num_repos
        )
    """)
    results = pd.read_sql(topInsightsSQL, self.database, params={'repo_group_id': repo_group_id, 'num_repos': num_repos})
    return results
