#SPDX-License-Identifier: MIT

#THIS FILE MIGHT BE UNNEEDED. DOUBLE CHECK AGAINST SREADSHEET FOR WHERE DEPS GO.

"""
Metrics that provide data about with insight detection and reporting
"""

import sqlalchemy as s
import pandas as pd
from augur.util import register_metric
#Need to import functions for finding languages stuff


@register_metric(type="repo_group_only")
def deps(self, repo_group_id, num_repos=6):
    """
    All dependancies in the project with the language for each.

    :return: DataFrame with deps
    """

    #THIS IS COPIED FROM OTHER METRIC FILE. PROBABLY DOESN'T WORK HERE
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
