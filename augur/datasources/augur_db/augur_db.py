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

    @annotate(tag='code-changes-lines')
    def code_changes_lines(self, repo_url, period='day', begin_date=None, end_date=None):
        """Returns a timeseries of code changes added and removed.

        :param repo_url: The repository's URL
        :param period: To set the periodicity to 'day', 'week', 'month', or 'year', defaults to 'day'
        :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
        :param end_date: Specifies the end date, defaults to datetime.now()
        :return: DataFrame of code changes/period
        """
        if not begin_date:
            begin_date = '1970-1-1 00:00:00'
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        code_changes_lines_SQL = s.sql.text("""
            SELECT date_trunc(:period, cmt_author_date::DATE) as commit_date, SUM(cmt_added) AS added, SUM(cmt_removed) as removed
            FROM commits
            WHERE repo_id = (SELECT repo_id FROM repo WHERE repo_git LIKE :repourl LIMIT 1)
            AND cmt_author_date BETWEEN :begin_date AND :end_date
            GROUP BY commit_date
            ORDER BY commit_date;
        """)

        results = pd.read_sql(code_changes_lines_SQL, self.db, params={'repourl': '%{}%'.format(repo_url), 'period': period,
                                                                        'begin_date': begin_date, 'end_date': end_date})
        return results

    @annotate(tag='issues-new')
    def issues_new(self, repo_url, period='day', begin_date=None, end_date=None):
        """Returns a timeseries of new issues opened.

        :param repo_url: The repository's URL
        :param period: To set the periodicity to 'day', 'week', 'month', or 'year', defaults to 'day'
        :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
        :param end_date: Specifies the end date, defaults to datetime.now()
        :return: DataFrame of new issues/period
        """
        if not begin_date:
            begin_date = '1970-1-1 00:00:00'
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        issues_new_SQL = s.sql.text("""
            SELECT date_trunc(:period, created_at::DATE) as issue_date, COUNT(issue_id) as issues
            FROM issues
            WHERE repo_id = (SELECT repo_id FROM repo WHERE repo_git LIKE :repourl LIMIT 1)
            AND created_at BETWEEN :begin_date AND :end_date
            GROUP BY issue_date
            ORDER  BY issue_date;
        """)

        results = pd.read_sql(issues_new_SQL, self.db, params={'repourl': '%{}%'.format(repo_url), 'period': period,
                                                                'begin_date': begin_date, 'end_date': end_date})
        return results


    @annotate(tag='issues-closed')
    def issues_closed(self, repo_url, period='day', begin_date=None, end_date=None):
        """Returns a timeseries of issues closed.

        :param repo_url: The repository's URL
        :param period: To set the periodicity to 'day', 'week', 'month', or 'year', defaults to 'day'
        :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
        :param end_date: Specifies the end date, defaults to datetime.now()
        :return: DataFrame of issues closed/period
        """
        if not begin_date:
            begin_date = '1970-1-1 00:00:00'
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        issues_closed_SQL = s.sql.text("""
            SELECT date_trunc(:period, closed_at::DATE) as issue_close_date, COUNT(issue_id) as issues
            FROM issues
            WHERE repo_id = (SELECT repo_id FROM repo WHERE repo_git LIKE :repourl LIMIT 1)
            AND closed_at IS NOT NULL AND closed_at BETWEEN :begin_date AND :end_date
            GROUP BY issue_close_date
            ORDER BY issue_close_date;
        """)

        results = pd.read_sql(issues_closed_SQL, self.db, params={'repourl': '%{}%'.format(repo_url), 'period': period,
                                                                'begin_date': begin_date, 'end_date': end_date})
        return results

    @annotate(tag='issue-duration')
    def issue_duration(self, repo_url):
        """Returns the duration of each issue.

        :param repo_url: The repository's URL
        :return: DataFrame of issue id with the corresponding duration
        """
        issue_duration_SQL = s.sql.text("""
            SELECT issue_id, (closed_at - created_at) AS duration
            FROM issues
            WHERE repo_id = (SELECT repo_id FROM repo WHERE repo_git LIKE :repourl LIMIT 1)
            AND closed_at IS NOT NULL
            ORDER BY issue_id;
        """)

        results = pd.read_sql(issue_duration_SQL, self.db, params={'repourl': f'%{repo_url}%'})
        return results

    @annotate(tag='issue-backlog')
    def issues_backlog(self, repo_url):
        """Returns number of issues currently open.

        :param repo_url: The repository's URL
        :return: DataFrame of count of issues currently open.
        """
        issues_backlog_SQL = s.sql.text("""
            SELECT COUNT(*)
            FROM issues
            WHERE repo_id = (SELECT repo_id FROM repo WHERE repo_git LIKE :repourl LIMIT 1)
            AND issue_state='open'
        """)

        result = pd.read_sql(issues_backlog_SQL, self.db, params={'repourl': f'%{repo_url}%'})
        return result

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