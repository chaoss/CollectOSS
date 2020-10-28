#SPDX-License-Identifier: MIT
"""
Metrics that provide data about releases
"""

import datetime
import sqlalchemy as s
import pandas as pd
from augur.util import register_metric

@register_metric()
def releases(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """ Returns a timeseris of new releases created

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of new releases/period
    """
    if not begin_date:
        begin_date = '1970-1-1'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    if not repo_id:
        releases_SQL = s.sql.text("""
            SELECT
                res.repo_name,
                res.release_id,
                res.release_name,
                res.release_description,
                res.release_author,
                res.release_created_at,
                res.release_published_at,
                res.release_updated_at,
                res.release_is_draft,
                res.release_is_prerelease,
                res.release_tag_name,
                res.release_url,
                COUNT(res)
            FROM (
                SELECT
                    releases.*
                    repo.repo_name
                FROM
                    releases LEFT JOIN repo ON releases.repo_id = repo.repo_id
                WHERE
                    repo.repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id )
                    AND releases.tag_only = False
            ) as res
            GROUP BY releases.repo_id, releases.release_id
            ORDER BY releases.release_published_at DESC
        """)

        results = pd.read_sql(releases_SQL, self.database,
                              params={'period': period, 'repo_group_id': repo_group_id,
                                      'begin_date': begin_date, 'end_date': end_date })
        return results

    else:
        releases_SQL = s.sql.text("""
            SELECT
                repo.repo_name,
                releases.release_id,
                releases.release_name,
                releases.release_description,
                releases.release_author,
                releases.release_created_at,
                releases.release_published_at,
                releases.release_updated_at,
                releases.release_is_draft,
                releases.release_is_prerelease,
                releases.release_tag_name,
                releases.release_url,
                COUNT(releases)
            FROM
                releases LEFT JOIN repo ON releases.repo_id = repo.repo_id
            WHERE releases.tag_only = False
            GROUP BY repo.repo_id, releases.release_id
            ORDER BY releases.release_published_at DESC
        """)

        results = pd.read_sql(releases_SQL, self.database,
                              params={'period': period, 'repo_id': repo_id,
                                      'begin_date': begin_date, 'end_date': end_date})
        return results

@register_metric()
def tag_only_releases(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """ Returns a timeseris of new tags that are considered releases
    without an official release being published

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of new releases/period
    """
    if not begin_date:
        begin_date = '1970-1-1'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    if not repo_id:
        releases_SQL = s.sql.text("""
            SELECT
                res.repo_name,
                res.release_id,
                res.release_name,
                res.release_author,
                res.release_created_at,
                res.release_tag_name,
                COUNT(res)
            FROM (
                SELECT
                    releases.*
                    repo.repo_name
                FROM
                    releases LEFT JOIN repo ON releases.repo_id = repo.repo_id
                WHERE
                    repo.repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id )
                    AND releases.tag_only = True
            ) as res
            GROUP BY releases.repo_id, releases.release_id
            ORDER BY releases.release_published_at DESC
        """)

        results = pd.read_sql(releases_SQL, self.database,
                              params={'period': period, 'repo_group_id': repo_group_id,
                                      'begin_date': begin_date, 'end_date': end_date })
        return results

    else:
        releases_SQL = s.sql.text("""
            SELECT
                repo.repo_name,
                releases.release_id,
                releases.release_name,
                releases.release_author,
                releases.release_created_at,
                releases.release_tag_name,
                COUNT(releases)
            FROM
                releases LEFT JOIN repo ON releases.repo_id = repo.repo_id
            WHERE releases.tag_only = True
            GROUP BY repo.repo_id, releases.release_id
            ORDER BY releases.release_published_at DESC
        """)

        results = pd.read_sql(releases_SQL, self.database,
                              params={'period': period, 'repo_id': repo_id,
                                      'begin_date': begin_date, 'end_date': end_date})
        return results

def create_release_metrics(metrics):
    add_metrics(metrics, __name__)