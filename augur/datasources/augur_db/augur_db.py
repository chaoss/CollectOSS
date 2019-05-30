#SPDX-License-Identifier: MIT
"""
Data source that uses the Augur relational database of GitHub activity. 
"""

import pandas as pd
import sqlalchemy as s
import numpy as np
import re
import datetime
from augur import logger
from augur.util import annotate

class Augur(object):
    """Uses the Augur database to return dataframes with interesting GitHub indicators"""

    def __init__(self, user, password, host, port, dbname, schema):
        """
        Connect to Augur

        :param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the Augur database
        """
        print(user, password, host, port, dbname, schema)
        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
        )

        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(schema)})

        logger.debug('GHTorrent: Connecting to {} schema of {}:{}/{} as {}'.format(schema, host, port, dbname, user))
        
        # try:
        #     self.userid('howderek')
        # except Exception as e:
        #     logger.error("Could not connect to GHTorrent database. Error: " + str(e))

    #####################################
    ###           EVOLUTION           ###
    #####################################

    @annotate(tag='code-changes')
    def code_changes(self, repo_url, period='day', begin_date=None, end_date=None):
        """
        Returns a timeseries of the count of code commits.

        :param repo_url: The repository's URL
        :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
        :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
        :param end_date: Specifies the end date, defaults to datetime.now()
        :return: DataFrame of commits/period
        """
        if not begin_date:
            begin_date = '1970-1-1 00:00:00:00'
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        code_changes_SQL = s.sql.text("""
            SELECT date_trunc(:period, cmt_committer_date::DATE) as commit_date, COUNT(cmt_id) 
            FROM commits
            WHERE repo_id = (SELECT repo_id FROM repo WHERE repo_git LIKE :repourl LIMIT 1) 
            AND cmt_committer_date BETWEEN :begin_date AND :end_date
            GROUP BY commit_date
            ORDER BY commit_date;
        """)

        results = pd.read_sql(code_changes_SQL, self.db, params={'repourl': '%{}%'.format(repo_url), 'period': period, 
                                                                'begin_date': begin_date, 'end_date': end_date})
        return results

    @annotate(tag='pull-requests-merge-contributor-new')
    def pull_requests_merge_contributor_new(self, repo_url, period='day', begin_date=None, end_date=None):
        """
        Returns a timeseries of the count of persons contributing with an accepted commit for the first time.

        :param repo_url: The repository's URL
        :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
        :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
        :param end_date: Specifies the end date, defaults to datetime.now()
        :return: DataFrame of persons/period
        """
        if not begin_date:
            begin_date = '1970-1-1 00:00:00:00'
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        commitNewContributor = s.sql.text("""
            SELECT date_trunc(:period, new_date::DATE) as commit_date, 
            COUNT(cmt_ght_author_id)
            FROM ( SELECT cmt_ght_author_id, MIN(TO_TIMESTAMP(cmt_author_date,'YYYY-MM-DD')) AS new_date
            FROM commits WHERE
            repo_id = (SELECT repo_id FROM repo WHERE repo_git LIKE :repourl LIMIT 1)
            AND TO_TIMESTAMP(cmt_author_date,'YYYY-MM-DD') BETWEEN :begin_date AND :end_date AND cmt_ght_author_id IS NOT NULL
            GROUP BY cmt_ght_author_id
            ) as abc GROUP BY commit_date
        """)

        results = pd.read_sql(commitNewContributor, self.db, params={'repourl': '%{}%'.format(repo_url), 'period': period,
                                                                     'begin_date': begin_date, 'end_date': end_date})
        return results

    @annotate(tag='issues-first-time-opened')
    def issues_first_time_opened(self, repo_url, period='day', begin_date=None, end_date=None):
        """
        Returns a timeseries of the count of persons opening an issue for the first time.

        :param repo_url: The repository's URL
        :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
        :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
        :param end_date: Specifies the end date, defaults to datetime.now()
        :return: DataFrame of persons/period
        """

        if not begin_date:
            begin_date = '1970-1-1 00:00:00:00'
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        issueNewContributor = s.sql.text("""
            SELECT
                date_trunc(:period, new_date::DATE) as issue_date,
                COUNT(cntrb_id)
            FROM (
                SELECT
                    cntrb_id,
                    MIN(created_at) AS new_date
                FROM
                    issues
                WHERE
                    repo_id = (SELECT repo_id FROM repo WHERE repo_git LIKE :repourl LIMIT 1)
                    AND created_at BETWEEN :begin_date AND :end_date
                GROUP BY cntrb_id
            ) as abc
            GROUP BY issue_date
            ORDER BY issue_date
        """)

        results = pd.read_sql(issueNewContributor, self.db, params={'repourl': '%{}%'.format(repo_url), 'period': period,
                                                                    'begin_date': begin_date, 'end_date': end_date})
        return results

    @annotate(tag='sub-projects')
    def sub_projects(self, repo_url, begin_date=None, end_date=None):
        """
        Returns number of sub-projects

        :param repo_url: the repository's URL
        """
        if not begin_date:
            begin_date = '1970-1-1 00:00:01'
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sub_projectsSQL = s.sql.text("""
            SELECT COUNT(*) - 1 AS sub_protject_count
            FROM repo
            WHERE repo_group_id = (
            SELECT repo_group_id
            FROM repo
            WHERE  repo_id = (SELECT repo_id FROM repo WHERE repo_git LIKE :repourl LIMIT 1))
            AND repo_added BETWEEN :begin_date AND :end_date
        """)

        results = pd.read_sql(sub_projectsSQL, db, params={'repourl': '%{}%'.format(repo_url),
                                                           'begin_date': begin_date, 'end_date': end_date})
        return results

    #####################################
    ###         EXPERIMENTAL          ###
    #####################################

    @annotate(tag='lines-changed-by-author')
    def lines_changed_by_author(self, repo_url):
        """
        Returns number of lines changed per author per day 

        :param repo_url: the repository's URL
        """
        linesChangedByAuthorSQL = s.sql.text("""
            SELECT cmt_author_email, cmt_author_date, cmt_author_affiliation as affiliation, 
                SUM(cmt_added) as additions, SUM(cmt_removed) as deletions, SUM(cmt_whitespace) as whitespace
            FROM commits
            WHERE repo_id = (SELECT repo_id FROM repo WHERE repo_git LIKE :repourl LIMIT 1)
            GROUP BY repo_id, cmt_author_date, cmt_author_affiliation, cmt_author_email
            ORDER BY cmt_author_date ASC;
        """)
        results = pd.read_sql(linesChangedByAuthorSQL, self.db, params={"repourl": '%{}%'.format(repo_url)})
        return results