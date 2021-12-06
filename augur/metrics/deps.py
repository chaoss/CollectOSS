#SPDX-License-Identifier: MIT
"""
Metrics that provide data about software dependencies. 
"""

import sqlalchemy as s
import pandas as pd
from augur.util import register_metric
@register_metric()
def deps(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """
    Returns a list of all the dependencies in a project/repo/repo_group.

    :param repo_id: The repository's id
    :param repo_group_id: The repository's group id
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of persons/period
    """

    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if repo_id:

        depsSQL = s.sql.text("""
		SELECT
			augur_data.repo_dependencies.*,
			augur_data.repo_groups.repo_group_id 
		FROM
			augur_data.repo_dependencies,
			augur_data.repo_groups,
			augur_data.repo,
			( SELECT MAX ( date_trunc( 'day', augur_data.repo_dependencies.data_collection_date ) ) AS data_collection_date FROM repo_dependencies WHERE repo_id = repo_id ) C 
		WHERE
			repo_dependencies.repo_id = repo.repo_id 
			AND repo.repo_group_id = repo_groups.repo_group_id 
			AND date_trunc( 'day', repo_dependencies.data_collection_date ) = C.data_collection_date 
			AND repo_dependencies.repo_id = :repo_id
        """)

		results = pd.read_sql(depsSQL, self.database)    	

    else:

        depsSQL = s.sql.text("""
		SELECT
			augur_data.repo_dependencies.*,
			augur_data.repo_groups.repo_group_id 
		FROM
			augur_data.repo_dependencies,
			augur_data.repo_groups,
			augur_data.repo,
			( SELECT MAX ( date_trunc( 'day', augur_data.repo_dependencies.data_collection_date ) ) AS data_collection_date 
			FROM repo_dependencies, repo, repo_groups 
			WHERE repo.repo_group_id = repo_groups.repo_group_id and 
			repo_dependencies.repo_id = repo.repo_id and
				 repo_groups.repo_group_id = :repo_group_id ) C 
		WHERE
			repo_dependencies.repo_id = repo.repo_id 
			AND repo.repo_group_id = repo_groups.repo_group_id 
			AND date_trunc( 'day', repo_dependencies.data_collection_date ) = C.data_collection_date 
			AND repo.repo_group_id = :repo_group_id
        """)

		results = pd.read_sql(depsSQL, self.database)
    return results



